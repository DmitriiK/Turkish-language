import { isoCode } from '../countries'

export function Flag({ country }: { country: string }) {
  const iso = isoCode(country)
  if (!iso) return <span className="flag flag-unknown" aria-hidden="true" />
  return <span className={`flag fi fi-${iso}`} aria-hidden="true" />
}
