import { useEffect, useMemo, useState } from 'react'
import type { Dict, Lang } from '../i18n'
import { fasterThanShare, formatPace, formatTime, rankIn, type Runner } from '../stats'
import { Flag } from './Flag'

interface Props {
  all: Runner[]
  selection: Runner[]
  selected: Runner | null
  onSelect: (r: Runner | null) => void
  distanceKm: number
  lang: Lang
  t: Dict
}

function normalize(s: string): string {
  return s
    .toLocaleLowerCase('tr')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/ı/g, 'i')
}

function formatShare(lang: Lang, share: number): string {
  return share.toLocaleString(lang, { style: 'percent', maximumFractionDigits: 1 })
}

function runnerKey(r: Runner): string {
  return `${r.bib}-${r.name}`
}

function isInSelection(runner: Runner, selection: Runner[]): boolean {
  return selection.some((r) => runnerKey(r) === runnerKey(runner))
}

export function RunnerSearch({ all, selection, selected, onSelect, distanceKm, lang, t }: Props) {
  const [query, setQuery] = useState('')

  const index = useMemo(() => all.map((r) => ({ r, key: normalize(r.name) })), [all])

  const matches = useMemo(() => {
    const q = query.trim()
    if (!q) return []
    if (/^\d+$/.test(q)) return all.filter((r) => String(r.bib) === q)
    if (q.length < 2) return []
    const words = normalize(q).split(/[\s,]+/).filter(Boolean)
    return index.filter(({ key }) => words.every((w) => key.includes(w))).slice(0, 20).map(({ r }) => r)
  }, [query, all, index])

  const total = selection.filter((r) => r.seconds != null).length

  useEffect(() => {
    const forChart = matches.find((r) => r.seconds != null) ?? null
    const nextKey = forChart ? runnerKey(forChart) : ''
    const curKey = selected ? runnerKey(selected) : ''
    if (nextKey !== curKey) onSelect(forChart)
  }, [matches, onSelect, selected])

  const anyOutsideSelection = matches.some((r) => r.seconds != null && !isInSelection(r, selection))

  return (
    <section className="card">
      <h2>{t.findYou}</h2>
      <input
        className="search-input"
        placeholder={t.findPlaceholder}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          if (!e.target.value.trim()) onSelect(null)
        }}
      />
      {query.trim() && (
        <div className="matches">
          {matches.length === 0 ? (
            <p className="muted">{t.noMatches}</p>
          ) : (
            <>
              <div className="table-wrap">
                <table className="search-results-table">
                  <thead>
                    <tr>
                      <th>{t.bib}</th>
                      <th>{t.name}</th>
                      <th className="num">{t.time}</th>
                      <th className="num">{t.pacePerKm}</th>
                      <th className="num">{t.place}</th>
                      <th className="num">{t.betterThanShare}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {matches.map((r) => {
                      const hasTime = r.seconds != null
                      const rank = hasTime ? rankIn(selection, r.seconds!) : null
                      const share = hasTime ? fasterThanShare(selection, r.seconds!) : null
                      const inSel = isInSelection(r, selection)
                      const chartRow = selected && runnerKey(selected) === runnerKey(r)
                      return (
                        <tr
                          key={runnerKey(r)}
                          className={`${chartRow ? 'search-row-chart' : ''}${!inSel && hasTime ? ' search-row-outside' : ''}`}
                        >
                          <td className="num bib-cell">{r.bib}</td>
                          <td>
                            <span className="with-flag">
                              <Flag country={r.country} />
                              {r.name}
                            </span>
                          </td>
                          <td className="num">{hasTime ? formatTime(r.seconds) : (r.status ?? t.noTime)}</td>
                          <td className="num pace-line pace-line-normal">
                            {hasTime ? `${formatPace(r.seconds!, distanceKm)}` : '—'}
                          </td>
                          <td className="num">
                            {rank != null && total > 0 ? (
                              <>
                                {rank} <span className="muted small">/ {total}</span>
                              </>
                            ) : (
                              '—'
                            )}
                          </td>
                          <td className="num">
                            {share != null ? (
                              <span className="share-cell">
                                <b>{formatShare(lang, share)}</b>
                                <span className="percent-bar percent-bar-inline">
                                  <span className="percent-fill" style={{ width: `${share * 100}%` }} />
                                </span>
                              </span>
                            ) : (
                              '—'
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              {anyOutsideSelection && <p className="muted small">{t.notInSelection}</p>}
            </>
          )}
        </div>
      )}
    </section>
  )
}
