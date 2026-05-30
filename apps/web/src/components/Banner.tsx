import type { ReactNode } from 'react'

const variantStyles: Record<string, { bg: string; border: string; color: string }> = {
  info: { bg: 'var(--color-info-light)', border: 'color-mix(in srgb, var(--color-info) 25%, var(--color-info-light))', color: 'var(--color-info)' },
  warning: { bg: 'var(--color-warning-light)', border: 'color-mix(in srgb, var(--color-warning) 25%, var(--color-warning-light))', color: 'var(--color-warning)' },
  error: { bg: 'var(--color-error-light)', border: 'color-mix(in srgb, var(--color-error) 25%, var(--color-error-light))', color: 'var(--color-error)' },
  success: { bg: 'var(--color-success-light)', border: 'color-mix(in srgb, var(--color-success) 25%, var(--color-success-light))', color: 'var(--color-success)' },
}

interface BannerProps {
  variant: keyof typeof variantStyles
  children: ReactNode
  className?: string
}

export function Banner({ variant, children, className = '' }: BannerProps) {
  const s = variantStyles[variant]
  return (
    <div
      className={`rounded-xl p-4 mb-4 text-sm ${className}`}
      style={{ backgroundColor: s.bg, border: `1px solid ${s.border}`, color: s.color }}
    >
      {children}
    </div>
  )
}
