import type { ReactNode } from 'react'

const variantStyles: Record<string, { bg: string; color: string }> = {
  success: { bg: '#f0fdf4', color: '#16a34a' },
  warning: { bg: '#fffbeb', color: '#d97706' },
  error: { bg: '#fef2f2', color: '#dc2626' },
  info: { bg: '#eff6ff', color: '#2563eb' },
  amber: { bg: '#fef3c7', color: '#b45309' },
  muted: { bg: '#f5f4f0', color: '#78716c' },
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
