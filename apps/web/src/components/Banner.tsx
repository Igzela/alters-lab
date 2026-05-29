import type { ReactNode } from 'react'

const variantStyles: Record<string, { bg: string; border: string; color: string }> = {
  info: { bg: '#eff6ff', border: '#bfdbfe', color: '#2563eb' },
  warning: { bg: '#fffbeb', border: '#fde68a', color: '#d97706' },
  error: { bg: '#fef2f2', border: '#fecaca', color: '#dc2626' },
  success: { bg: '#f0fdf4', border: '#bbf7d0', color: '#16a34a' },
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
