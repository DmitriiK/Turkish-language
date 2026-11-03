import type { Dict } from '../i18n'
import type { DistanceKey } from '../stats'

/** Left-to-right order when Marathon is selected: 15.5K · Marathon · Wheelchair */
const DISTANCES: DistanceKey[] = ['15_5k', 'marathon', 'wheelchair']

interface Props {
  value: DistanceKey
  onChange: (d: DistanceKey) => void
  t: Dict
}

export function RaceSwitcher({ value, onChange, t }: Props) {
  const idx = DISTANCES.indexOf(value)
  const order: DistanceKey[] = [
    DISTANCES[(idx - 1 + DISTANCES.length) % DISTANCES.length],
    DISTANCES[idx],
    DISTANCES[(idx + 1) % DISTANCES.length],
  ]

  return (
    <div className="race-switcher" role="group" aria-label={t.distance}>
      {order.map((d) => {
        const active = d === value
        return (
          <button
            key={d}
            type="button"
            className={active ? 'race-switcher-active' : 'race-switcher-side'}
            aria-pressed={active}
            onClick={() => onChange(d)}
          >
            {t[d]}
          </button>
        )
      })}
    </div>
  )
}
