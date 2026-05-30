interface ProgressBarProps {
  value: number
  max?: number
  accent?: 'amber' | 'green' | 'red' | 'blue'
  label?: string
  className?: string
}

const accentColorVars: Record<string, string> = {
  amber: 'var(--color-accent)',
  green: 'var(--color-success)',
  red: 'var(--color-error)',
  blue: 'var(--color-info)',
}

export function ProgressBar({ value, max = 100, accent = 'amber', label, className = '' }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const color = accentColorVars[accent] || accentColorVars.amber

  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <div className="text-xs mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>{label}</div>
      )}
      <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-border)' }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}
