interface ProgressBarProps {
  value: number
  max?: number
  accent?: 'amber' | 'green' | 'red' | 'blue'
  label?: string
  className?: string
}

const accentColors: Record<string, string> = {
  amber: '#b45309',
  green: '#16a34a',
  red: '#dc2626',
  blue: '#2563eb',
}

export function ProgressBar({ value, max = 100, accent = 'amber', label, className = '' }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const color = accentColors[accent] || accentColors.amber

  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <div className="text-xs mb-1.5" style={{ color: '#78716c' }}>{label}</div>
      )}
      <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: '#e8e6e1' }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}
