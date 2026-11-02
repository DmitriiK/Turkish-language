import { useMemo, useState } from 'react'
import type { Dict } from '../i18n'
import { finishers, formatTime, normalPdf, type Runner, type Summary } from '../stats'

interface Props {
  runners: Runner[]
  summary: Summary
  highlight?: { seconds: number; label: string }
  t: Dict
}

const W = 860
const H = 320
const PAD = { left: 48, right: 16, top: 16, bottom: 40 }

function niceStep(raw: number): number {
  if (raw <= 1) return 1
  const mag = 10 ** Math.floor(Math.log10(raw))
  const norm = raw / mag
  return (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10) * mag
}

function pickBinSize(range: number): number {
  const candidates = [30, 60, 120, 180, 300, 600, 900, 1200, 1800]
  return candidates.find((c) => range / c <= 45) ?? 3600
}

export function Histogram({ runners, summary, highlight, t }: Props) {
  const [hover, setHover] = useState<number | null>(null)

  const chart = useMemo(() => {
    const times = finishers(runners).map((r) => r.seconds!)
    const min = Math.min(...times)
    const max = Math.max(...times)
    const bin = pickBinSize(Math.max(max - min, 60))
    const start = Math.floor(min / bin) * bin
    const nBins = Math.max(1, Math.ceil((max - start + 1) / bin))
    const counts = new Array<number>(nBins).fill(0)
    for (const s of times) counts[Math.min(nBins - 1, Math.floor((s - start) / bin))]++

    const end = start + nBins * bin
    const curve: [number, number][] = []
    const steps = 160
    for (let i = 0; i <= steps; i++) {
      const x = start + ((end - start) * i) / steps
      curve.push([x, normalPdf(x, summary.mean, summary.std) * times.length * bin])
    }
    const peak = Math.max(...counts, ...curve.map((c) => c[1]))
    const yStep = niceStep(peak / 4)
    const yMax = Math.ceil((peak * 1.05) / yStep) * yStep
    const yTicks: number[] = []
    for (let v = yStep; v <= yMax; v += yStep) yTicks.push(v)
    return { bin, start, end, counts, curve, yMax, yTicks }
  }, [runners, summary])

  const innerW = W - PAD.left - PAD.right
  const innerH = H - PAD.top - PAD.bottom
  const x = (s: number) => PAD.left + ((s - chart.start) / (chart.end - chart.start)) * innerW
  const y = (v: number) => PAD.top + innerH - (v / chart.yMax) * innerH
  const barW = innerW / chart.counts.length

  const ticks = useMemo(() => {
    const span = chart.end - chart.start
    const step = [300, 600, 900, 1800, 3600, 7200].find((s) => span / s <= 8) ?? 7200
    const out: number[] = []
    for (let s = Math.ceil(chart.start / step) * step; s <= chart.end; s += step) out.push(s)
    return out
  }, [chart])

  const path = chart.curve.map(([cx, cy], i) => `${i ? 'L' : 'M'}${x(cx).toFixed(1)},${y(cy).toFixed(1)}`).join(' ')
  const hoverFrom = hover != null ? chart.start + hover * chart.bin : 0

  return (
    <div className="histogram">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={t.distribution}>
        {chart.yTicks.map((v) => (
          <g key={v}>
            <line className="grid" x1={PAD.left} x2={W - PAD.right} y1={y(v)} y2={y(v)} />
            <text className="axis-label" x={PAD.left - 6} y={y(v) + 4} textAnchor="end">
              {v}
            </text>
          </g>
        ))}
        {chart.counts.map((c, i) => (
          <rect
            key={i}
            className={`bar ${hover === i ? 'bar-hover' : ''}`}
            x={PAD.left + i * barW + 0.5}
            y={y(c)}
            width={Math.max(barW - 1, 0.5)}
            height={PAD.top + innerH - y(c)}
            onMouseEnter={() => setHover(i)}
            onMouseLeave={() => setHover(null)}
          />
        ))}
        <path className="curve" d={path} />
        <line className="mean-line" x1={x(summary.mean)} x2={x(summary.mean)} y1={PAD.top} y2={PAD.top + innerH} />
        {highlight && highlight.seconds >= chart.start && highlight.seconds <= chart.end && (
          <g>
            <line className="you-line" x1={x(highlight.seconds)} x2={x(highlight.seconds)} y1={PAD.top} y2={PAD.top + innerH} />
            <text className="you-label" x={x(highlight.seconds) + 4} y={PAD.top + 12}>
              {highlight.label}
            </text>
          </g>
        )}
        <line className="axis" x1={PAD.left} x2={W - PAD.right} y1={PAD.top + innerH} y2={PAD.top + innerH} />
        {ticks.map((s) => (
          <text key={s} className="axis-label" x={x(s)} y={H - PAD.bottom + 18} textAnchor="middle">
            {formatTime(s).replace(/:00$/, '')}
          </text>
        ))}
      </svg>
      <div className="histogram-footer">
        <span className="legend"><span className="swatch swatch-bar" /> {t.runners}</span>
        <span className="legend"><span className="swatch swatch-curve" /> {t.normalFit}</span>
        <span className="legend"><span className="swatch swatch-mean" /> {t.average}</span>
        {hover != null && (
          <span className="hover-info">
            {formatTime(hoverFrom)} – {formatTime(hoverFrom + chart.bin)}: <b>{chart.counts[hover]}</b> {t.runners}
          </span>
        )}
      </div>
    </div>
  )
}
