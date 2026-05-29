import type { HTMLAttributes, ReactNode } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'raised'
  accent?: 'amber' | 'green' | 'red' | 'blue'
  children: ReactNode
  className?: string
}

const accentBorders: Record<string, string> = {
  amber: '#b45309',
  green: '#16a34a',
  red: '#dc2626',
  blue: '#2563eb',
}

export function Card({ variant = 'default', accent, children, className = '', ...rest }: CardProps) {
  return (
    <div
      className={`rounded-xl p-4 mb-4 ${className}`}
      style={{
        backgroundColor: variant === 'raised' ? '#f5f4f0' : '#ffffff',
        border: accent ? `1px solid ${accentBorders[accent]}30` : '1px solid #e8e6e1',
        borderLeft: accent ? `3px solid ${accentBorders[accent]}` : undefined,
        boxShadow: variant === 'raised' ? '0 1px 3px rgba(28,25,23,0.06)' : 'none',
      }}
      {...rest}
    >
      {children}
    </div>
  )
}
