import { formatPace, formatTime } from '../stats'

interface Props {
  seconds: number | null | undefined
  distanceKm: number
  paceLabel: string
  size?: 'big' | 'normal'
}

export function TimeWithPace({ seconds, distanceKm, paceLabel, size = 'normal' }: Props) {
  return (
    <div className="time-with-pace">
      <div className={size === 'big' ? 'big' : undefined}>{formatTime(seconds)}</div>
      {seconds != null && Number.isFinite(seconds) && (
        <div className="pace-line muted small">
          {formatPace(seconds, distanceKm)} {paceLabel}
        </div>
      )}
    </div>
  )
}
