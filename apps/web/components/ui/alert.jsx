import { cn } from '../../lib/utils'
export function Alert({ className, variant = 'default', ...props }) {
  const styles = {
    default: 'bg-gray-50 text-gray-800 border-gray-200',
    warning: 'bg-yellow-50 text-yellow-900 border-yellow-200',
    danger: 'bg-red-50 text-red-900 border-red-200',
  }
  return <div className={cn('rounded-md border p-3 text-sm', styles[variant] || styles.default, className)} {...props} />
}
