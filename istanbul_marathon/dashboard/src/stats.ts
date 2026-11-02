export type DistanceKey = 'marathon' | '15_5k' | 'wheelchair'

export interface Runner {
  bib: number | string
  name: string
  gender: string
  country: string
  age: string | null
  seconds: number | null
  status: string | null
}

type RawRow = [number | string, string, string, string, string | null, number | null, string | null]

export async function loadDistance(key: DistanceKey): Promise<Runner[]> {
  const res = await fetch(`${import.meta.env.BASE_URL}data/${key}.json`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data: { rows: RawRow[] } = await res.json()
  return data.rows.map(([bib, name, gender, country, age, seconds, status]) => ({
    bib,
    name,
    gender,
    country,
    age,
    seconds,
    status,
  }))
}

export function genderOrder(g: string): number {
  return g === 'M' ? 0 : g === 'F' ? 1 : 2
}

export function formatTime(seconds: number | null | undefined): string {
  if (seconds == null || !Number.isFinite(seconds)) return '—'
  const s = Math.round(seconds)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

export interface Summary {
  count: number
  mean: number
  median: number
  std: number
  best: number
  top3: Runner[]
}

export function finishers(runners: Runner[]): Runner[] {
  return runners.filter((r) => r.seconds != null)
}

export function summarize(runners: Runner[]): Summary | null {
  const done = finishers(runners).sort((a, b) => a.seconds! - b.seconds!)
  if (done.length === 0) return null
  const times = done.map((r) => r.seconds!)
  const mean = times.reduce((a, b) => a + b, 0) / times.length
  const variance = times.reduce((a, t) => a + (t - mean) ** 2, 0) / times.length
  const mid = Math.floor(times.length / 2)
  const median = times.length % 2 ? times[mid] : (times[mid - 1] + times[mid]) / 2
  return {
    count: done.length,
    mean,
    median,
    std: Math.sqrt(variance),
    best: times[0],
    top3: done.slice(0, 3),
  }
}

export function normalPdf(x: number, mean: number, std: number): number {
  if (std === 0) return 0
  const z = (x - mean) / std
  return Math.exp(-0.5 * z * z) / (std * Math.sqrt(2 * Math.PI))
}

/** Share of finishers in `runners` that are strictly slower than `seconds`. */
export function fasterThanShare(runners: Runner[], seconds: number): number {
  const done = finishers(runners)
  if (done.length === 0) return 0
  const slower = done.filter((r) => r.seconds! > seconds).length
  return slower / done.length
}

export function rankIn(runners: Runner[], seconds: number): number {
  return finishers(runners).filter((r) => r.seconds! < seconds).length + 1
}
