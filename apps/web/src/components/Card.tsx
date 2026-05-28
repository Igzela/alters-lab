import type { ReactNode } from 'react'

const accentBorders: Record<string, string> = {
  green: '#0ae448',
  pink: '#f100cb',
  orange: '#ff8709',
  lilac: '#9d95ff',
  blue: '#00bae2',
}

interface CardProps {
  variant?: 'default' | 'raised'
  accent?: keyof typeof accentBorders
  children: ReactNode
  className?: string
}

export function Card({ variant = 'default', accent, children, className = '' }: CardProps) {
  const bg = variant === 'raised' ? '#242624' : '#1a1c1a'
  const borderStyle = accent
    ? `1px solid ${accentBorders[accent]}40`
    : '1px solid #42433d'

  return (
    <div
      className={`rounded-xl p-4 mb-4 ${className}`}
      style={{
        backgroundColor: bg,
        border: borderStyle,
        borderLeft: accent ? `3px solid ${accentBorders[accent]}` : borderStyle,
      }}
    >
      {children}
    </div>
  )
}
