'use client'
import { Suspense } from 'react'
import Link from 'next/link'

export default function NotFound() {
  return (
    <Suspense fallback={<div className="text-sm text-muted-foreground">Loading…</div>}>
      <div className="container mx-auto max-w-2xl py-12">
        <h1 className="text-2xl font-semibold mb-2">404 Not Found</h1>
        <p className="text-sm text-muted-foreground mb-4">The page you are looking for does not exist.</p>
        <Link className="underline text-sm" href="/">Go Home</Link>
      </div>
    </Suspense>
  )
}
