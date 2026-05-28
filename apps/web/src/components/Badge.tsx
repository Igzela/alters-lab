import type { ReactNode } from 'react'

const variantStyles: Record<string, { bg: string; color: string }> = {
  success: { bg: 'rgba(10, 228, 72, 0.15)', color: '#0ae448' },
  warning: { bg: 'rgba(255, 135, 9, 0.15)', color: '#ff8709' },
  error: { bg: 'rgba(255, 68, 68, 0.15)', color: '#ff4444' },
  info: { bg: 'rgba(0, 186, 226, 0.15)', color: '#00bae2' },
  muted: { bg: 'rgba(124, 124, 111, 0.15)', color: '#7c7c6f' },
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
      className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-[9999px] ${className}`}
      style={{ backgroundColor: s.bg, color: s.color }}
    >
      {children}
    </span>
  )
}
