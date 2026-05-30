import type { ReactNode } from 'react'

const variantStyles: Record<string, { bg: string; color: string }> = {
  success: { bg: 'var(--color-success-light)', color: 'var(--color-success)' },
  warning: { bg: 'var(--color-warning-light)', color: 'var(--color-warning)' },
  error: { bg: 'var(--color-error-light)', color: 'var(--color-error)' },
  info: { bg: 'var(--color-info-light)', color: 'var(--color-info)' },
  amber: { bg: 'var(--color-accent-light)', color: 'var(--color-accent)' },
  muted: { bg: 'var(--color-surface-raised)', color: 'var(--color-text-secondary)' },
}

interface BadgeProps {
  variant?: keyof typeof variantStyles
  children: ReactNode
  className?: string
}

export function Badge({ variant = 'muted', children, className = '' }: BadgeProps) {
  const s = variantStyles[variant] || variantStyles.muted
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full ${className}`}
      style={{ backgroundColor: s.bg, color: s.color }}
    >
      {children}
    </span>
  )
}
