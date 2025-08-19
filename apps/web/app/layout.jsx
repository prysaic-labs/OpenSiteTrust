import "./globals.css";
import Link from 'next/link'
import LangSwitcher from '../components/lang-switcher'
import { Suspense } from 'react'

export const metadata = {
  title: 'OpenSiteTrust',
  description: 'Open, explainable website trust scoring (MVP)'
};

export default function RootLayout({ children }) {
  const version = process.env.NEXT_PUBLIC_VERSION || 'v0.11';
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground">
        <header className="border-b">
          <div className="container flex h-12 items-center justify-between">
            <div className="font-semibold">OpenSiteTrust</div>
            <div className="text-sm text-muted-foreground flex items-center gap-3">
              <span>MVP Preview · {version}</span>
              <Suspense fallback={<nav className="flex items-center gap-2 text-xs" aria-label="language-switcher"/>}>
                <LangSwitcher />
              </Suspense>
            </div>
          </div>
        </header>
        <main className="container py-6">
          {children}
        </main>
        <footer className="border-t">
          <div className="container py-4 text-sm text-muted-foreground">© OpenSiteTrust Contributors</div>
        </footer>
      </body>
    </html>
  );
}
