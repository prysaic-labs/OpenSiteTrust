import { cn } from '../../lib/utils'
export function Badge({ className, variant = 'secondary', ...props }) {
  const base = 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold'
  const variants = {
    default: 'bg-gray-900 text-white',
    secondary: 'border-transparent bg-gray-100 text-gray-900',
    outline: 'text-gray-900',
  }
  return <span className={cn(base, variants[variant] || variants.secondary, className)} {...props} />
}
