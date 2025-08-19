'use client'
import Link from 'next/link'
import { usePathname, useSearchParams } from 'next/navigation'

export default function LangSwitcher() {
  const pathname = usePathname()
  const sp = useSearchParams()

  const makeHref = (lang) => {
    const params = new URLSearchParams(sp?.toString?.() || '')
    params.set('lang', lang)
    const q = params.toString()
    return q ? `${pathname}?${q}` : pathname
  }

  return (
    <nav className="flex items-center gap-2">
      <Link className="underline text-xs" href={makeHref('en')}>EN</Link>
      <Link className="underline text-xs" href={makeHref('zh')}>中文</Link>
      <Link className="underline text-xs" href={makeHref('zh-Hant')}>繁體</Link>
      <Link className="underline text-xs" href={makeHref('ja')}>日本語</Link>
      <Link className="underline text-xs" href={makeHref('es')}>Español</Link>
    </nav>
  )
}
