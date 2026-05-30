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

const accentBorderVars: Record<string, string> = {
  amber: 'var(--color-accent)',
  green: 'var(--color-success)',
  red: 'var(--color-error)',
  blue: 'var(--color-info)',
}

export function Card({ variant = 'default', accent, children, className = '', ...rest }: CardProps) {
  return (
    <div
      className={`rounded-xl p-4 mb-4 ${className}`}
      style={{
        backgroundColor: variant === 'raised' ? 'var(--color-surface-raised)' : 'var(--color-surface)',
        border: accent ? `1px solid var(--color-border)` : '1px solid var(--color-border)',
        borderLeft: accent ? `3px solid ${accentBorderVars[accent]}` : undefined,
        boxShadow: variant === 'raised' ? '0 1px 3px rgba(28,25,23,0.06)' : 'none',
      }}
      {...rest}
    >
      {children}
    </div>
  )
}
