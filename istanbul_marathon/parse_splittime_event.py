#!/usr/bin/env python3
"""Parse iPico Wiz / SplitTime live results into JSON."""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BASE = "https://results.splittime.nl/results/GetData.aspx"

OUTPUT_FILES = {
    "Marathon": "marathon.json",
    "15.5K": "15_5k.json",
    "Wheelchair": "wheelchair.json",
}


class RowParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_row = False
        self.in_td = False
        self.row_cells: list[str] = []
        self.rows: list[list[str]] = []
        self.cell_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        cls = dict(attrs).get("class", "")
        if tag == "tr" and cls == "TableResultRow":
            self.in_row = True
            self.row_cells = []
        elif self.in_row and tag == "td":
            self.in_td = True
            self.cell_buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self.in_td:
            self.in_td = False
            text = "".join(self.cell_buf).strip().replace("\xa0", "")
            self.row_cells.append(text)
        elif tag == "tr" and self.in_row:
            self.in_row = False
            if len(self.row_cells) >= 7:
                self.rows.append(self.row_cells)

    def handle_data(self, data: str) -> None:
        if self.in_td:
            self.cell_buf.append(data)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_rows(html: str) -> list[list[str]]:
    parser = RowParser()
    parser.feed(html)
    return parser.rows


def split_category(cat: str, include_age: bool) -> tuple[str, str | None]:
    cat = cat.strip()
    if cat.startswith("MALE"):
        gender, age = "M", cat[4:] or None
    elif cat.startswith("FEMALE"):
        gender, age = "F", cat[6:] or None
    else:
        return cat, None
    if not include_age:
        age = None
    return gender, age


def row_to_entry(cells: list[str], include_age: bool) -> dict:
    bib_raw = cells[1]
    gender, age_category = split_category(cells[3], include_age)
    entry: dict = {
        "bib": int(bib_raw) if bib_raw.isdigit() else bib_raw,
        "name": cells[2],
        "gender": gender,
        "country": cells[4],
        "mat_time": cells[6],
    }
    if age_category:
        entry["age_category"] = age_category
    return entry


def scrape_distance(event_id: int, distance: str) -> list[dict]:
    include_age = distance in ("Marathon", "Wheelchair")
    encoded = urllib.parse.quote(distance)
    results: list[dict] = []

    page = 0
    while True:
        url = (
            f"{BASE}?EventID={event_id}&Distance={encoded}"
            f"&ShowAll=True&Page={page}"
        )
        html = fetch(url)
        rows = parse_rows(html)
        if not rows:
            if page == 0:
                url = f"{BASE}?EventID={event_id}&Distance={encoded}&ShowAll=False"
                html = fetch(url)
                rows = parse_rows(html)
            break
        for cells in rows:
            results.append(row_to_entry(cells, include_age))
        if len(rows) < 101:
            break
        page += 1

    return results


def write_distance_file(
    out_dir: Path,
    event_id: int,
    distance: str,
    results: list[dict],
) -> Path:
    filename = OUTPUT_FILES.get(distance, f"{distance.lower().replace('.', '_')}.json")
    out_path = out_dir / filename
    payload = {
        "event_id": event_id,
        "source": (
            f"https://results.splittime.nl/results/ShowEvent.aspx"
            f"?EventID={event_id}"
        ),
        "distance": distance,
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event_id", type=int, nargs="?", default=12849)
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument(
        "--distances",
        nargs="*",
        default=["Marathon", "15.5K", "Wheelchair"],
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for distance in args.distances:
        print(f"Scraping {distance}...", flush=True)
        results = scrape_distance(args.event_id, distance)
        out_path = write_distance_file(
            args.output_dir, args.event_id, distance, results
        )
        print(f"  {len(results)} finishers -> {out_path.name}", flush=True)


if __name__ == "__main__":
    main()
