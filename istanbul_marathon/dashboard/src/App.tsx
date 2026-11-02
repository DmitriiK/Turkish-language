import { useEffect, useMemo, useState } from 'react'
import { AggregateTable, type Dimension } from './components/AggregateTable'
import { CountrySelect } from './components/CountrySelect'
import { Flag } from './components/Flag'
import { Histogram } from './components/Histogram'
import { PaceHistogram } from './components/PaceHistogram'
import { RunnerSearch } from './components/RunnerSearch'
import { TimeWithPace } from './components/TimeWithPace'
import { countryName } from './countries'
import { DICTS, LANGS, type Lang } from './i18n'
import {
  genderOrder,
  loadDistance,
  RACE_DISTANCE_KM,
  runnerPaceSeconds,
  summarize,
  summarizePace,
  type CentralMetric,
  type DistanceKey,
  type Runner,
} from './stats'

const DISTANCES: DistanceKey[] = ['marathon', '15_5k', 'wheelchair']
const SOURCE_URL = 'https://results.splittime.nl/results/ShowEvent.aspx?EventID=12849'

function initialLang(): Lang {
  const saved = localStorage.getItem('lang')
  if (saved === 'tr' || saved === 'en' || saved === 'ru') return saved
  const nav = navigator.language.slice(0, 2)
  return nav === 'tr' || nav === 'ru' ? nav : 'en'
}

function initialCentralMetric(): CentralMetric {
  return localStorage.getItem('centralMetric') === 'median' ? 'median' : 'mean'
}

export default function App() {
  const [lang, setLang] = useState<Lang>(initialLang)
  const [data, setData] = useState<Record<DistanceKey, Runner[]> | null>(null)
  const [error, setError] = useState(false)
  const [distance, setDistance] = useState<DistanceKey>('marathon')
  const [age, setAge] = useState('all')
  const [gender, setGender] = useState('all')
  const [country, setCountry] = useState('all')
  const [selected, setSelected] = useState<Runner | null>(null)
  const [centralMetric, setCentralMetric] = useState<CentralMetric>(initialCentralMetric)
  const t = DICTS[lang]

  useEffect(() => {
    localStorage.setItem('centralMetric', centralMetric)
  }, [centralMetric])

  useEffect(() => {
    localStorage.setItem('lang', lang)
    document.documentElement.lang = lang
    document.title = `${t.title} — ${t.subtitle}`
  }, [lang, t])

  useEffect(() => {
    Promise.all(DISTANCES.map(loadDistance))
      .then(([marathon, k15, wheelchair]) => setData({ marathon, '15_5k': k15, wheelchair }))
      .catch(() => setError(true))
  }, [])

  const runners = data?.[distance] ?? []
  const hasAge = distance === 'marathon'

  const ageOptions = useMemo(
    () => [...new Set(runners.map((r) => r.age).filter((a): a is string => !!a))].sort(),
    [runners],
  )

  const genderOptions = useMemo(
    () => [...new Set(runners.map((r) => r.gender))].sort((a, b) => genderOrder(a) - genderOrder(b)),
    [runners],
  )

  const beforeCountry = useMemo(
    () =>
      runners.filter(
        (r) => (!hasAge || age === 'all' || r.age === age) && (gender === 'all' || r.gender === gender),
      ),
    [runners, hasAge, age, gender],
  )

  const countryOptions = useMemo(() => {
    const counts = new Map<string, number>()
    for (const r of beforeCountry) {
      if (r.seconds != null) counts.set(r.country, (counts.get(r.country) ?? 0) + 1)
    }
    return [...counts].map(([code, count]) => ({ code, count })).sort((a, b) => b.count - a.count)
  }, [beforeCountry])

  const selection = useMemo(
    () => (country === 'all' ? beforeCountry : beforeCountry.filter((r) => r.country === country)),
    [beforeCountry, country],
  )

  const distanceKm = RACE_DISTANCE_KM[distance]
  const summary = useMemo(() => summarize(selection), [selection])
  const paceSummary = useMemo(() => summarizePace(selection, distanceKm), [selection, distanceKm])

  const dimensions = useMemo(() => {
    const dims: Dimension[] = []
    if (gender === 'all') dims.push('gender')
    if (hasAge && age === 'all') dims.push('age')
    if (country === 'all') dims.push('country')
    return dims
  }, [gender, hasAge, age, country])

  const totals = useMemo(() => {
    if (!data) return null
    const all = DISTANCES.flatMap((d) => data[d])
    return {
      finishers: all.filter((r) => r.seconds != null).length,
      countries: new Set(all.map((r) => r.country).filter((c) => c !== '-')).size,
    }
  }, [data])

  const changeDistance = (d: DistanceKey) => {
    setDistance(d)
    setAge('all')
    setGender('all')
    setCountry('all')
    setSelected(null)
  }

  const genderLabel = (g: string) => (g === 'M' ? t.male : g === 'F' ? t.female : t.unknownGender)

  return (
    <div className="page">
      <header className="hero">
        <div className="hero-side hero-side-left" aria-hidden="true">
          <img src={`${import.meta.env.BASE_URL}hero-bridge.jpg`} alt="" />
        </div>
        <div className="hero-center">
          <div className="lang-switch" role="group">
            {LANGS.map((l) => (
              <button
                key={l.id}
                type="button"
                className={lang === l.id ? 'active' : ''}
                onClick={() => setLang(l.id)}
              >
                {l.label}
              </button>
            ))}
          </div>
          <div className="hero-text">
            <p className="hero-date">{t.heroDate}</p>
            <h1>{t.title}</h1>
            <p className="hero-sub">{t.subtitle}</p>
            <p className="hero-desc">{t.heroText}</p>
            {totals && (
              <div className="hero-stats">
                <div>
                  <b>{totals.finishers.toLocaleString(lang)}</b> {t.totalFinishers}
                </div>
                <div>
                  <b>{totals.countries}</b> {t.countriesCount}
                </div>
              </div>
            )}
          </div>
        </div>
        <div className="hero-side hero-side-right" aria-hidden="true">
          <img src={`${import.meta.env.BASE_URL}hero.png`} alt="" />
        </div>
      </header>

      <main className="content">
        {error && <p className="card error">{t.loadError}</p>}
        {!data && !error && <p className="card muted">{t.loading}</p>}

        {data && (
          <>
            <section className="card filters">
              <div className="filter">
                <label>{t.distance}</label>
                <div className="segmented">
                  {DISTANCES.map((d) => (
                    <button
                      key={d}
                      type="button"
                      className={distance === d ? 'active' : ''}
                      onClick={() => changeDistance(d)}
                    >
                      {t[d]}
                    </button>
                  ))}
                </div>
              </div>

              {hasAge && (
                <div className="filter">
                  <label htmlFor="age">{t.ageGroup}</label>
                  <select id="age" value={age} onChange={(e) => setAge(e.target.value)}>
                    <option value="all">{t.all}</option>
                    {ageOptions.map((a) => (
                      <option key={a} value={a}>
                        {a}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="filter">
                <label>{t.gender}</label>
                <div className="segmented">
                  {['all', ...genderOptions].map((g) => (
                    <button
                      key={g}
                      type="button"
                      className={gender === g ? 'active' : ''}
                      onClick={() => setGender(g)}
                    >
                      {g === 'all' ? t.all : genderLabel(g)}
                    </button>
                  ))}
                </div>
              </div>

              <div className="filter">
                <label>{t.country}</label>
                <CountrySelect value={country} options={countryOptions} lang={lang} t={t} onChange={setCountry} />
              </div>

              <div className="filter">
                <label>{t.centralMetric}</label>
                <div className="segmented">
                  <button
                    type="button"
                    className={centralMetric === 'mean' ? 'active' : ''}
                    onClick={() => setCentralMetric('mean')}
                  >
                    {t.averageShort}
                  </button>
                  <button
                    type="button"
                    className={centralMetric === 'median' ? 'active' : ''}
                    onClick={() => setCentralMetric('median')}
                  >
                    {t.medianShort}
                  </button>
                </div>
              </div>
            </section>

            <section className="card">
              <h2>{t.stats}</h2>
              {!summary ? (
                <p className="muted">{t.noResults}</p>
              ) : (
                <div className="stats-grid">
                  <div className="stat">
                    <div className="muted">{t.count}</div>
                    <div className="big">{summary.count.toLocaleString(lang)}</div>
                  </div>
                  <div className={`stat${centralMetric === 'mean' ? ' stat-active' : ''}`}>
                    <div className="muted">{t.average}</div>
                    <TimeWithPace
                      seconds={summary.mean}
                      distanceKm={distanceKm}
                      paceLabel={t.pacePerKm}
                      size="big"
                    />
                  </div>
                  <div className={`stat${centralMetric === 'median' ? ' stat-active' : ''}`}>
                    <div className="muted">{t.median}</div>
                    <TimeWithPace
                      seconds={summary.median}
                      distanceKm={distanceKm}
                      paceLabel={t.pacePerKm}
                      size="big"
                    />
                  </div>
                  <div className="stat top3">
                    <div className="muted">{t.top3}</div>
                    <ol>
                      {summary.top3.map((r) => (
                        <li key={`${r.bib}-${r.name}`}>
                          <span className="with-flag" title={countryName(r.country, lang)}>
                            <Flag country={r.country} />
                            {r.name}
                          </span>
                          <TimeWithPace
                            seconds={r.seconds}
                            distanceKm={distanceKm}
                            paceLabel={t.pacePerKm}
                          />
                        </li>
                      ))}
                    </ol>
                  </div>
                </div>
              )}
            </section>

            {summary && paceSummary && (
              <section className="card charts-card">
                <div className="charts-grid">
                  <div className="chart-block">
                    <h2>{t.distribution}</h2>
                    <p className="muted small">{t.distributionHint}</p>
                    <Histogram
                      runners={selection}
                      summary={summary}
                      centralMetric={centralMetric}
                      t={t}
                      highlight={
                        selected?.seconds != null
                          ? { seconds: selected.seconds, label: selected.name.split(',')[0] }
                          : undefined
                      }
                    />
                  </div>
                  <div className="chart-block">
                    <h2>{t.paceDistribution}</h2>
                    <p className="muted small">{t.paceDistributionHint}</p>
                    <PaceHistogram
                      runners={selection}
                      summary={paceSummary}
                      distanceKm={distanceKm}
                      centralMetric={centralMetric}
                      t={t}
                      highlight={
                        selected?.seconds != null
                          ? {
                              paceSecPerKm: runnerPaceSeconds(selected, distanceKm),
                              label: selected.name.split(',')[0],
                            }
                          : undefined
                      }
                    />
                  </div>
                </div>
              </section>
            )}

            <RunnerSearch
              key={distance}
              all={runners}
              selection={selection}
              selected={selected}
              onSelect={setSelected}
              distanceKm={distanceKm}
              lang={lang}
              t={t}
            />

            <AggregateTable
              runners={selection}
              dimensions={dimensions}
              distanceKm={distanceKm}
              centralMetric={centralMetric}
              lang={lang}
              t={t}
            />

            <footer className="footer muted small">
              {t.dataSource}: <a href={SOURCE_URL}>results.splittime.nl</a>
            </footer>
          </>
        )}
      </main>
    </div>
  )
}
