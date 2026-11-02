import { useEffect, useMemo, useState } from 'react'
import { countryName } from '../countries'
import type { Dict, Lang } from '../i18n'
import {
  fasterPaceShare,
  fasterThanShare,
  formatPace,
  formatTime,
  rankByPace,
  rankIn,
  runnerPaceSeconds,
  type Runner,
} from '../stats'
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

function MetricColumn({
  label,
  value,
  valueClassName,
  rank,
  total,
  share,
  lang,
  t,
}: {
  label: string
  value: string
  valueClassName?: string
  rank: number
  total: number
  share: number
  lang: Lang
  t: Dict
}) {
  return (
    <div className="runner-metric-col">
      <div className="runner-metric-label">{label}</div>
      <div className={`runner-metric-value ${valueClassName ?? ''}`}>{value}</div>
      <div className="runner-metric-place">
        {t.place}:{' '}
        <b>
          {rank} / {total}
        </b>
      </div>
      <div className="runner-metric-percentile muted small">
        {t.betterThanShare} <b>{formatShare(lang, share)}</b>
      </div>
      <div className="percent-bar">
        <div className="percent-fill" style={{ width: `${share * 100}%` }} />
      </div>
    </div>
  )
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

  useEffect(() => {
    if (matches.length === 1) onSelect(matches[0])
  }, [matches, onSelect])

  const inSelection = selected ? selection.some((r) => runnerKey(r) === runnerKey(selected)) : false
  const total = selection.filter((r) => r.seconds != null).length

  const timeStats =
    selected?.seconds != null
      ? {
          rank: rankIn(selection, selected.seconds),
          share: fasterThanShare(selection, selected.seconds),
        }
      : null

  const paceStats =
    selected?.seconds != null
      ? (() => {
          const pace = runnerPaceSeconds(selected, distanceKm)
          return {
            pace,
            rank: rankByPace(selection, pace, distanceKm),
            share: fasterPaceShare(selection, pace, distanceKm),
          }
        })()
      : null

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
      {query.trim() && (
        <div className="matches">
          {matches.length === 0 ? (
            <p className="muted">{t.noMatches}</p>
          ) : (
            <>
              {!selected && matches.length > 1 && <p className="muted small">{t.selectRunnerHint}</p>}
              <ul>
                {matches.map((r) => (
                  <li key={runnerKey(r)}>
                    <button
                      type="button"
                      className={selected && runnerKey(selected) === runnerKey(r) ? 'match-selected' : ''}
                      onClick={() => onSelect(r)}
                    >
                      <span className="bib">#{r.bib}</span>
                      <span className="with-flag">
                        <Flag country={r.country} />
                        {r.name}
                      </span>
                      <span className="muted match-times">
                        {r.seconds != null ? (
                          <>
                            {formatTime(r.seconds)}
                            <span className="pace-line pace-line-normal">
                              {formatPace(r.seconds, distanceKm)} {t.pacePerKm}
                            </span>
                          </>
                        ) : (
                          r.status ?? t.noTime
                        )}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
      {selected && (
        <div className="you-card">
          <div className="you-header">
            <div className="you-name">{selected.name}</div>
            <div className="muted with-flag">
              <Flag country={selected.country} />
              {countryName(selected.country, lang)} · {t.bib} {selected.bib}
              {selected.age ? ` · ${selected.age}` : ''}
            </div>
            <div className="muted small">{t.percentileInSelection}</div>
          </div>

          {selected.seconds != null && timeStats && paceStats && total > 0 ? (
            <div className="runner-metrics-columns">
              <MetricColumn
                label={t.time}
                value={formatTime(selected.seconds)}
                rank={timeStats.rank}
                total={total}
                share={timeStats.share}
                lang={lang}
                t={t}
              />
              <MetricColumn
                label={t.pacePerKm}
                value={`${formatPace(paceStats.pace, 1)}`}
                valueClassName="pace-line pace-line-big"
                rank={paceStats.rank}
                total={total}
                share={paceStats.share}
                lang={lang}
                t={t}
              />
            </div>
          ) : (
            <div className="big">{selected.status ?? t.noTime}</div>
          )}

          {!inSelection && selected.seconds != null && <p className="muted small">{t.notInSelection}</p>}
        </div>
      )}
    </section>
  )
}
