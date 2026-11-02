import { useEffect, useMemo, useRef, useState } from 'react'
import { countryName } from '../countries'
import type { Dict, Lang } from '../i18n'
import { Flag } from './Flag'

interface Props {
  value: string
  options: { code: string; count: number }[]
  lang: Lang
  t: Dict
  onChange: (code: string) => void
}

export function CountrySelect({ value, options, lang, t, onChange }: Props) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const close = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])

  const visible = useMemo(() => {
    const q = query.trim().toLocaleLowerCase(lang)
    return options
      .map((o) => ({ ...o, label: countryName(o.code, lang) }))
      .filter((o) => !q || o.label.toLocaleLowerCase(lang).includes(q) || o.code.toLowerCase().includes(q))
  }, [options, query, lang])

  const pick = (code: string) => {
    onChange(code)
    setOpen(false)
    setQuery('')
  }

  return (
    <div className="country-select" ref={rootRef}>
      <button type="button" className="select-button" onClick={() => setOpen((o) => !o)}>
        {value === 'all' ? (
          <span>{t.all}</span>
        ) : (
          <span className="with-flag">
            <Flag country={value} />
            {countryName(value, lang)}
          </span>
        )}
        <span className="caret">▾</span>
      </button>
      {open && (
        <div className="dropdown">
          <input
            autoFocus
            className="dropdown-search"
            placeholder={t.searchCountry}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <ul>
            <li>
              <button type="button" className={value === 'all' ? 'active' : ''} onClick={() => pick('all')}>
                {t.all}
              </button>
            </li>
            {visible.map((o) => (
              <li key={o.code}>
                <button type="button" className={value === o.code ? 'active' : ''} onClick={() => pick(o.code)}>
                  <span className="with-flag">
                    <Flag country={o.code} />
                    {o.label}
                  </span>
                  <span className="muted">{o.count}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
