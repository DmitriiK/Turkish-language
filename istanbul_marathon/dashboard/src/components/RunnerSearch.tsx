import { useMemo, useState } from 'react'
import { countryName } from '../countries'
import type { Dict, Lang } from '../i18n'
import { fasterThanShare, formatTime, rankIn, type Runner } from '../stats'
import { Flag } from './Flag'

interface Props {
  all: Runner[]
  selection: Runner[]
  selected: Runner | null
  onSelect: (r: Runner | null) => void
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

export function RunnerSearch({ all, selection, selected, onSelect, lang, t }: Props) {
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

  const inSelection = selected ? selection.includes(selected) : false
  const share = selected?.seconds != null ? fasterThanShare(selection, selected.seconds) : null
  const rank = selected?.seconds != null ? rankIn(selection, selected.seconds) : null
  const total = selection.filter((r) => r.seconds != null).length

  return (
    <section className="card">
      <h2>{t.findYou}</h2>
      <input
        className="search-input"
        placeholder={t.findPlaceholder}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          onSelect(null)
        }}
      />
      {query.trim() && !selected && (
        <div className="matches">
          {matches.length === 0 ? (
            <p className="muted">{t.noMatches}</p>
          ) : (
            <ul>
              {matches.map((r) => (
                <li key={`${r.bib}-${r.name}`}>
                  <button type="button" onClick={() => onSelect(r)}>
                    <span className="bib">#{r.bib}</span>
                    <span className="with-flag">
                      <Flag country={r.country} />
                      {r.name}
                    </span>
                    <span className="muted">{r.seconds != null ? formatTime(r.seconds) : r.status ?? t.noTime}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {selected && (
        <div className="you-card">
          <div className="you-main">
            <div>
              <div className="you-name">{selected.name}</div>
              <div className="muted with-flag">
                <Flag country={selected.country} />
                {countryName(selected.country, lang)} · {t.bib} {selected.bib}
                {selected.age ? ` · ${selected.age}` : ''}
              </div>
            </div>
            <div className="you-time">
              <div className="muted">{t.yourResult}</div>
              <div className="big">{selected.seconds != null ? formatTime(selected.seconds) : selected.status ?? t.noTime}</div>
            </div>
          </div>
          {share != null && rank != null && (
            <div className="you-stats">
              <div>
                <div className="muted">{t.place}</div>
                <div className="big">
                  {rank} <span className="muted small">/ {total}</span>
                </div>
              </div>
              <div className="grow">
                <div className="muted">
                  {t.fasterThan}{' '}
                  <b>{share.toLocaleString(lang, { style: 'percent', maximumFractionDigits: 1 })}</b>
                </div>
                <div className="percent-bar">
                  <div className="percent-fill" style={{ width: `${share * 100}%` }} />
                </div>
              </div>
            </div>
          )}
          {!inSelection && selected.seconds != null && <p className="muted small">{t.notInSelection}</p>}
        </div>
      )}
    </section>
  )
}
