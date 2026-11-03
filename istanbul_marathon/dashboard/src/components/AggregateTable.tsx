import { Fragment, useMemo, useState } from 'react'
import { countryName } from '../countries'
import type { Dict, Lang } from '../i18n'
import { TimeWithPace } from './TimeWithPace'
import { genderOrder, medianOf, type CentralMetric, type Runner } from '../stats'
import { Flag } from './Flag'

export type Dimension = 'gender' | 'age' | 'country'

interface Props {
  runners: Runner[]
  dimensions: Dimension[]
  distanceKm: number
  centralMetric: CentralMetric
  lang: Lang
  t: Dict
}

interface Node {
  id: string
  dim: Dimension
  value: string
  count: number
  mean: number
  median: number
  best: number
  children: Node[]
  /** Sorted fastest-first; rendered when this aggregate leaf is expanded */
  leafRunners?: Runner[]
}

function keyOf(r: Runner, dim: Dimension): string {
  if (dim === 'gender') return r.gender
  if (dim === 'age') return r.age ?? '—'
  return r.country
}

function sortedFinishers(runners: Runner[]): Runner[] {
  return [...runners].sort((a, b) => a.seconds! - b.seconds! || String(a.bib).localeCompare(String(b.bib)))
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
    const isLeaf = rest.length === 0
    nodes.push({
      id,
      dim,
      value,
      count: rs.length,
      mean: times.reduce((a, b) => a + b, 0) / times.length,
      median: medianOf(times),
      best: Math.min(...times),
      children: isLeaf ? [] : build(rs, rest, id),
      leafRunners: isLeaf ? sortedFinishers(rs) : undefined,
    })
  }
  if (dim === 'country') nodes.sort((a, b) => b.count - a.count)
  else if (dim === 'gender') nodes.sort((a, b) => genderOrder(a.value) - genderOrder(b.value))
  else nodes.sort((a, b) => a.value.localeCompare(b.value))
  return nodes
}

function isExpandable(n: Node): boolean {
  return n.children.length > 0 || (n.leafRunners?.length ?? 0) > 0
}

function findNode(nodes: Node[], id: string): Node | undefined {
  for (const n of nodes) {
    if (n.id === id) return n
    const inChild = findNode(n.children, id)
    if (inChild) return inChild
  }
}

function collectExpandableIdsUnder(node: Node): string[] {
  const ids: string[] = []
  const visit = (n: Node) => {
    if (isExpandable(n)) ids.push(n.id)
    for (const c of n.children) visit(c)
  }
  visit(node)
  return ids
}

export function AggregateTable({ runners, dimensions, distanceKm, centralMetric, lang, t }: Props) {
  const centralLabel = centralMetric === 'mean' ? t.average : t.median
  const tree = useMemo(
    () => build(runners.filter((r) => r.seconds != null), dimensions, ''),
    [runners, dimensions],
  )
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const toggle = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
        const node = findNode(tree, id)
        if (node) {
          for (const cid of collectExpandableIdsUnder(node)) next.delete(cid)
        }
      } else {
        next.add(id)
      }
      return next
    })

  const runnerLabel = (r: Runner, rank: number) => (
    <span className="runner-leaf-label">
      <span className="runner-rank">{rank}.</span>
      {r.name}
      <span className="muted small">
        {' '}
        #{r.bib}
      </span>
    </span>
  )

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

  const renderNodes = (nodes: Node[], depth: number): JSX.Element[] =>
    nodes.map((n) => {
      const isOpen = expanded.has(n.id)
      const expandable = isExpandable(n)
      return (
        <Fragment key={n.id}>
          <tr className={`depth-${depth}`}>
            <td style={{ paddingLeft: 12 + depth * 22 }}>
              {expandable ? (
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
              <TimeWithPace
                seconds={centralMetric === 'mean' ? n.mean : n.median}
                distanceKm={distanceKm}
                paceLabel={t.pacePerKm}
              />
            </td>
            <td className="num">
              <TimeWithPace seconds={n.best} distanceKm={distanceKm} paceLabel={t.pacePerKm} />
            </td>
          </tr>
          {isOpen && n.children.length > 0 ? renderNodes(n.children, depth + 1) : null}
          {isOpen && n.leafRunners
            ? n.leafRunners.map((r, i) => (
                <tr key={`${n.id}/runner/${i}/${r.bib}`} className={`depth-${depth + 1} runner-row`}>
                  <td style={{ paddingLeft: 12 + (depth + 1) * 22 }}>
                    <span className="toggle-spacer" />
                    {runnerLabel(r, i + 1)}
                  </td>
                  <td className="num">—</td>
                  <td className="num">
                    <TimeWithPace seconds={r.seconds} distanceKm={distanceKm} paceLabel={t.pacePerKm} />
                  </td>
                  <td className="num">—</td>
                </tr>
              ))
            : null}
        </Fragment>
      )
    })

  if (dimensions.length === 0) return null

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>{t.breakdown}</h2>
          <p className="muted small">{t.breakdownHint}</p>
        </div>
        <div className="button-row">
          <button
            type="button"
            className="ghost"
            disabled={expanded.size === 0}
            onClick={() => setExpanded(new Set())}
          >
            {t.collapse}
          </button>
        </div>
      </div>
      <div className="table-wrap">
        <table className="agg-table">
          <thead>
            <tr>
              <th>{t.group}</th>
              <th className="num">{t.count}</th>
              <th className="num">{centralLabel}</th>
              <th className="num">{t.best}</th>
            </tr>
          </thead>
          <tbody>{renderNodes(tree, 0)}</tbody>
        </table>
      </div>
    </section>
  )
}
