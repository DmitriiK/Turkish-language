import { useMemo, useState } from 'react'
import { countryName } from '../countries'
import type { Dict, Lang } from '../i18n'
import { TimeWithPace } from './TimeWithPace'
import { genderOrder, type Runner } from '../stats'
import { Flag } from './Flag'

export type Dimension = 'gender' | 'age' | 'country'

interface Props {
  runners: Runner[]
  dimensions: Dimension[]
  distanceKm: number
  lang: Lang
  t: Dict
}

interface Node {
  id: string
  dim: Dimension
  value: string
  count: number
  mean: number
  best: number
  children: Node[]
}

function keyOf(r: Runner, dim: Dimension): string {
  if (dim === 'gender') return r.gender
  if (dim === 'age') return r.age ?? '—'
  return r.country
}

function build(runners: Runner[], dims: Dimension[], prefix: string): Node[] {
  if (dims.length === 0) return []
  const [dim, ...rest] = dims
  const groups = new Map<string, Runner[]>()
  for (const r of runners) {
    const k = keyOf(r, dim)
    if (!groups.has(k)) groups.set(k, [])
    groups.get(k)!.push(r)
  }
  const nodes: Node[] = []
  for (const [value, rs] of groups) {
    const times = rs.map((r) => r.seconds!)
    const id = `${prefix}/${value}`
    nodes.push({
      id,
      dim,
      value,
      count: rs.length,
      mean: times.reduce((a, b) => a + b, 0) / times.length,
      best: Math.min(...times),
      children: build(rs, rest, id),
    })
  }
  if (dim === 'country') nodes.sort((a, b) => b.count - a.count)
  else if (dim === 'gender') nodes.sort((a, b) => genderOrder(a.value) - genderOrder(b.value))
  else nodes.sort((a, b) => a.value.localeCompare(b.value))
  return nodes
}

function collectIds(nodes: Node[], out: string[] = []): string[] {
  for (const n of nodes) {
    if (n.children.length) {
      out.push(n.id)
      collectIds(n.children, out)
    }
  }
  return out
}

export function AggregateTable({ runners, dimensions, distanceKm, lang, t }: Props) {
  const tree = useMemo(
    () => build(runners.filter((r) => r.seconds != null), dimensions, ''),
    [runners, dimensions],
  )
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const toggle = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })

  const label = (n: Node) => {
    if (n.dim === 'gender') return n.value === 'M' ? t.male : n.value === 'F' ? t.female : t.unknownGender
    if (n.dim === 'age') return n.value
    return (
      <span className="with-flag">
        <Flag country={n.value} />
        {countryName(n.value, lang)}
      </span>
    )
  }

  const rows: JSX.Element[] = []
  const walk = (nodes: Node[], depth: number) => {
    for (const n of nodes) {
      const isOpen = expanded.has(n.id)
      rows.push(
        <tr key={n.id} className={`depth-${depth}`}>
          <td style={{ paddingLeft: 12 + depth * 22 }}>
            {n.children.length ? (
              <button type="button" className="toggle" onClick={() => toggle(n.id)} aria-expanded={isOpen}>
                {isOpen ? '−' : '+'}
              </button>
            ) : (
              <span className="toggle-spacer" />
            )}
            {label(n)}
          </td>
          <td className="num">{n.count}</td>
          <td className="num">
            <TimeWithPace seconds={n.mean} distanceKm={distanceKm} paceLabel={t.pacePerKm} />
          </td>
          <td className="num">
            <TimeWithPace seconds={n.best} distanceKm={distanceKm} paceLabel={t.pacePerKm} />
          </td>
        </tr>,
      )
      if (isOpen) walk(n.children, depth + 1)
    }
  }
  walk(tree, 0)

  if (dimensions.length === 0) return null

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>{t.breakdown}</h2>
          <p className="muted small">{t.breakdownHint}</p>
        </div>
        <div className="button-row">
          <button type="button" className="ghost" onClick={() => setExpanded(new Set(collectIds(tree)))}>
            {t.expandAll}
          </button>
          <button type="button" className="ghost" onClick={() => setExpanded(new Set())}>
            {t.collapseAll}
          </button>
        </div>
      </div>
      <div className="table-wrap">
        <table className="agg-table">
          <thead>
            <tr>
              <th>{t.group}</th>
              <th className="num">{t.count}</th>
              <th className="num">{t.average}</th>
              <th className="num">{t.best}</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
  )
}
