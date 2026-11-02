import type { Lang } from './i18n'

// Results use IOC-style codes; flags and Intl.DisplayNames need ISO 3166 codes.
const IOC_TO_ISO: Record<string, string> = {
  AFG: 'af', ALB: 'al', ALG: 'dz', ARG: 'ar', AUS: 'au', AUT: 'at', AZE: 'az',
  BEL: 'be', BIH: 'ba', BLR: 'by', BOT: 'bw', BRA: 'br', BRN: 'bh', BUL: 'bg',
  BUR: 'bf', CAN: 'ca', CGO: 'cg', CHI: 'cl', CHN: 'cn', CMR: 'cm', COL: 'co',
  CRC: 'cr', CRO: 'hr', CUB: 'cu', CYP: 'cy', CZE: 'cz', DEN: 'dk', DOM: 'do',
  ECU: 'ec', EGY: 'eg', ENG: 'gb-eng', ERI: 'er', ESP: 'es', EST: 'ee', ETH: 'et',
  FIN: 'fi', FRA: 'fr', GBR: 'gb', GEO: 'ge', GEQ: 'gq', GER: 'de', GRE: 'gr',
  GRL: 'gl', GUA: 'gt', GUI: 'gn', HAI: 'ht', HKG: 'hk', HUN: 'hu', INA: 'id',
  IND: 'in', IRI: 'ir', IRL: 'ie', IRQ: 'iq', ISL: 'is', ISR: 'il', ITA: 'it',
  JER: 'je', JOR: 'jo', JPN: 'jp', KAZ: 'kz', KEN: 'ke', KGZ: 'kg', KOR: 'kr',
  KOS: 'xk', KSA: 'sa', KUW: 'kw', LAT: 'lv', LBA: 'ly', LBR: 'lr', LES: 'ls',
  LIB: 'lb', LTU: 'lt', LUX: 'lu', MAR: 'ma', MAS: 'my', MDA: 'md', MEX: 'mx',
  MGL: 'mn', MKD: 'mk', MLI: 'ml', MNE: 'me', MRI: 'mu', MRQ: 'mq', NED: 'nl',
  NGR: 'ng', NOR: 'no', NZL: 'nz', OMN: 'om', PAK: 'pk', PER: 'pe', PHI: 'ph',
  PLE: 'ps', POL: 'pl', POR: 'pt', QAT: 'qa', ROM: 'ro', RSA: 'za', RUS: 'ru',
  SAU: 'sa', SCG: 'rs', SCO: 'gb-sct', SEN: 'sn', SER: 'rs', SIN: 'sg', SLO: 'si',
  SRI: 'lk', SSU: 'ss', SUD: 'sd', SUI: 'ch', SVK: 'sk', SWE: 'se', SYR: 'sy',
  THA: 'th', TJK: 'tj', TKM: 'tm', TKS: 'tc', TPE: 'tw', TRI: 'tt', TUN: 'tn',
  TUR: 'tr', UAE: 'ae', UGA: 'ug', UKR: 'ua', USA: 'us', UZB: 'uz', VEN: 've',
  VIE: 'vn', WAL: 'gb-wls', YEM: 'ye', ZAM: 'zm', ZIM: 'zw',
}

const SUBDIVISION_NAMES: Record<string, Record<Lang, string>> = {
  'gb-eng': { en: 'England', tr: 'İngiltere', ru: 'Англия' },
  'gb-sct': { en: 'Scotland', tr: 'İskoçya', ru: 'Шотландия' },
  'gb-wls': { en: 'Wales', tr: 'Galler', ru: 'Уэльс' },
}

const UNKNOWN_NAME: Record<Lang, string> = {
  en: 'Not specified',
  tr: 'Belirtilmemiş',
  ru: 'Не указана',
}

const displayNames: Partial<Record<Lang, Intl.DisplayNames>> = {}

export function isoCode(ioc: string): string | undefined {
  return IOC_TO_ISO[ioc]
}

export function countryName(ioc: string, lang: Lang): string {
  const iso = IOC_TO_ISO[ioc]
  if (!iso) return UNKNOWN_NAME[lang]
  if (SUBDIVISION_NAMES[iso]) return SUBDIVISION_NAMES[iso][lang]
  if (iso === 'xk') return { en: 'Kosovo', tr: 'Kosova', ru: 'Косово' }[lang]
  displayNames[lang] ??= new Intl.DisplayNames([lang], { type: 'region' })
  return displayNames[lang]!.of(iso.toUpperCase()) ?? ioc
}
