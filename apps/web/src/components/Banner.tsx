import type { ReactNode } from 'react'

const variantStyles: Record<string, { bg: string; border: string; color: string }> = {
  info: { bg: 'rgba(0, 186, 226, 0.08)', border: 'rgba(0, 186, 226, 0.2)', color: '#00bae2' },
  warning: { bg: 'rgba(255, 135, 9, 0.08)', border: 'rgba(255, 135, 9, 0.2)', color: '#ff8709' },
  error: { bg: 'rgba(255, 68, 68, 0.08)', border: 'rgba(255, 68, 68, 0.2)', color: '#ff4444' },
  success: { bg: 'rgba(10, 228, 72, 0.08)', border: 'rgba(10, 228, 72, 0.2)', color: '#0ae448' },
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
