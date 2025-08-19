import * as React from 'react'
export function Progress({ value = 0 }) {
  const v = Math.max(0, Math.min(100, value))
  return (
    <div className="h-2 w-full rounded bg-gray-200">
      <div className="h-2 rounded bg-emerald-500" style={{ width: `${v}%` }} />
    </div>
  )
}
