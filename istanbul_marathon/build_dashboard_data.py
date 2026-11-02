#!/usr/bin/env python3
"""Convert scraped results into compact JSON for the dashboard.

Each row is [bib, name, gender, country, age_category, seconds, status].
Rows without a finish time get seconds = null and a status such as DNF/DQ/DNS.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "dashboard" / "public" / "data"
FILES = {
    "marathon": "marathon.json",
    "15_5k": "15_5k.json",
    "wheelchair": "wheelchair.json",
}


def to_seconds(value: str) -> int | None:
    if not re.fullmatch(r"\d+(:\d\d)+", value):
        return None
    seconds = 0
    for part in value.split(":"):
        seconds = seconds * 60 + int(part)
    return seconds


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for key, filename in FILES.items():
        source = json.loads((HERE / filename).read_text(encoding="utf-8"))
        rows = [
            [
                r["bib"],
                r.get("name", ""),
                r["gender"],
                r["country"],
                r.get("age_category"),
                to_seconds(r["mat_time"]),
                None if to_seconds(r["mat_time"]) is not None else (r["mat_time"] or None),
            ]
            for r in source["results"]
        ]
        payload = {"distance": source["distance"], "rows": rows}
        out_path = OUT_DIR / f"{key}.json"
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        print(f"{out_path.relative_to(HERE)}: {len(rows)} rows")


if __name__ == "__main__":
    main()
