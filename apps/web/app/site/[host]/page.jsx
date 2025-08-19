'use client'
import { useEffect, useState, useMemo, useMemo as useM, useCallback } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card'
import { Badge } from '../../../components/ui/badge'
import { Progress } from '../../../components/ui/progress'
import { Separator } from '../../../components/ui/separator'
import { Alert } from '../../../components/ui/alert'
import { Button } from '../../../components/ui/button'
import { useLang, t } from '../../../lib/i18n'
import { Suspense } from 'react'

function SitePageContent({ params }) {
  const { host: rawHost } = params
  const lang = useLang()
  const normalizeHost = useCallback((input) => {
    const t = (input || '').trim()
    if (!t) return ''
    try {
      const u = new URL(t.includes('://') ? t : `http://${t}`)
      return u.hostname
    } catch {
      const s = t.replace(/^[a-z]+:\/\//i, '')
      const i = s.indexOf('/')
      return i >= 0 ? s.slice(0, i) : s
    }
  }, [])
  const host = useM(() => normalizeHost(rawHost), [rawHost, normalizeHost])
  const [data, setData] = useState(null)
  const [explain, setExplain] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [label, setLabel] = useState('safe')
  const [reason, setReason] = useState('')

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const [r1, r2] = await Promise.all([
          fetch(`/v1/sites/${encodeURIComponent(host)}`, { cache: 'no-store' }),
          fetch(`/v1/sites/${encodeURIComponent(host)}/explain`, { cache: 'no-store' }),
        ])
        if (!r1.ok) throw new Error(`HTTP ${r1.status}`)
        const j1 = await r1.json()
        const j2 = r2.ok ? await r2.json() : null
        if (!cancelled) {
          setData(j1)
          setExplain(j2)
        }
      } catch (e) {
        if (!cancelled) setError(String(e))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [host])

  const gsbFlagged = useMemo(() => {
    const s = explain?.signals?.find?.(x => x.key === 'google_safe_browsing_flagged')
    return !!s?.value
  }, [explain])

  const levelColor = data?.level === 'green' ? 'bg-emerald-500' : data?.level === 'amber' ? 'bg-amber-500' : 'bg-red-500'

  return (
    <div className="container mx-auto max-w-4xl py-6">
  <h1 className="mb-4 text-2xl font-semibold">{t('site', lang)}: {host}</h1>
      {loading && <div className="text-sm text-gray-500">Loading…</div>}
      {error && <div className="text-sm text-red-600">{error}</div>}
      {data && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className={`inline-block h-3 w-3 rounded-full ${levelColor}`} />
                <span className="text-2xl font-bold">{data.score}</span>
                <Badge>{data.level}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-500">{t('updatedAt', lang)}: {new Date(data.updated_at).toLocaleString()}</div>
              <div className="mt-4 space-y-3">
                <div>
                  <div className="mb-1 flex items-center justify-between text-sm"><span>{t('security', lang)}</span><span>{data.breakdown.S}</span></div>
                  <Progress value={Math.round(data.breakdown.S * 100)} />
                </div>
                <div>
                  <div className="mb-1 flex items-center justify-between text-sm"><span>{t('credibility', lang)}</span><span>{data.breakdown.C}</span></div>
                  <Progress value={Math.round(data.breakdown.C * 100)} />
                </div>
                <div>
                  <div className="mb-1 flex items-center justify-between text-sm"><span>{t('transparency', lang)}</span><span>{data.breakdown.T}</span></div>
                  <Progress value={Math.round(data.breakdown.T * 100)} />
                </div>
                <div>
                  <div className="mb-1 flex items-center justify-between text-sm">
          <span>{t('community', lang)}</span>
                    <span>
                      {data.breakdown.U}
                      {(!data.u_included || data.votes_total === 0) && (
            <span className="ml-2 text-gray-500">{t('noVotes', lang)}</span>
                      )}
                    </span>
                  </div>
                  <Progress value={Math.round((data.breakdown.U || 0) * 100)} />
                </div>
              </div>
              {gsbFlagged && (
                <Alert variant="danger" className="mt-4">{t('gsbAlert', lang)}</Alert>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('communityVote', lang)}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <label className="block text-sm font-medium">{t('label', lang)}</label>
                <select
                  className="w-full rounded-md border px-3 py-2 text-sm"
                  disabled={submitting}
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                >
                  <option value="safe">{t('safe', lang)}</option>
                  <option value="suspicious">{t('suspicious', lang)}</option>
                  <option value="danger">{t('danger', lang)}</option>
                </select>
                <label className="block text-sm font-medium">{t('reason', lang)}</label>
                <input
                  className="w-full rounded-md border px-3 py-2 text-sm"
                  disabled={submitting}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder={t('reason', lang)}
                />
                <Button
                  disabled={submitting}
                  onClick={async () => {
                    try {
                      setSubmitting(true)
                      const r = await fetch('/v1/votes', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ host, label, reason })
                      })
                      if (!r.ok) throw new Error(`HTTP ${r.status}`)
                      const r2 = await fetch(`/v1/sites/${encodeURIComponent(host)}`, { cache: 'no-store' })
                      if (r2.ok) setData(await r2.json())
                    } catch (e) {
                      alert('Vote failed: ' + e)
                    } finally {
                      setSubmitting(false)
                    }
                  }}
                >
                  {submitting ? t('submitting', lang) : t('submit', lang)}
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="md:col-span-3">
            <Separator className="my-2" />
            <div className="text-xs text-gray-500">API Docs: <a className="underline" href={`/v1/docs?lang=${encodeURIComponent(lang)}`}>/v1/docs</a> · Health: <a className="underline" href={`/v1/health?lang=${encodeURIComponent(lang)}`}>/v1/health</a></div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function SitePage(props) {
  return (
    <Suspense fallback={<div className="text-sm text-muted-foreground">Loading…</div>}>
      <SitePageContent {...props} />
    </Suspense>
  )
}
