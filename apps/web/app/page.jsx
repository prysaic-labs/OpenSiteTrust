'use client';
import { useRouter } from 'next/navigation';
import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useLang, t } from '../lib/i18n';
import { Suspense } from 'react';

function HomeContent() {
  const router = useRouter();
  const [host, setHost] = useState('example.com');
  const lang = useLang();

  const normalizeHost = useCallback((input) => {
    const t = (input || '').trim();
    if (!t) return '';
    try {
      const u = new URL(t.includes('://') ? t : `http://${t}`);
      return u.hostname;
    } catch {
      // Fallback: strip protocol-like prefix then cut at first '/'
      const s = t.replace(/^[a-z]+:\/\//i, '');
      const i = s.indexOf('/');
      return i >= 0 ? s.slice(0, i) : s;
    }
  }, []);

  const go = useCallback(() => {
    const h = normalizeHost(host);
    if (!h) {
      alert(t('invalidInput', lang));
      return;
    }
    router.push(`/site/${encodeURIComponent(h)}?lang=${encodeURIComponent(lang)}`);
  }, [host, normalizeHost, router]);

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>{t('title', lang)}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">{t('inputHelp', lang)}</p>
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') go(); }}
              placeholder={t('placeholder', lang)}
            />
            <Button onClick={go}>{t('view', lang)}</Button>
          </div>
          <div className="mt-3 text-xs text-muted-foreground">
            <div>{t('examples', lang)}: <a className="underline" href={`/site/example.com?lang=${encodeURIComponent(lang)}`}>example.com</a>, <a className="underline" href={`/site/foo.shop?lang=${encodeURIComponent(lang)}`}>foo.shop</a></div>
            <div className="mt-2"><a className="underline" href="/v1/docs">{t('apiDocs', lang)}</a> · <a className="underline" href="/v1/health">{t('apiHealth', lang)}</a></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="text-sm text-muted-foreground">Loading…</div>}>
      <HomeContent />
    </Suspense>
  );
}
