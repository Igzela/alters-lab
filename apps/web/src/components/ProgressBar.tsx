const accentColors: Record<string, string> = {
  green: '#0ae448',
  pink: '#f100cb',
  orange: '#ff8709',
  lilac: '#9d95ff',
  blue: '#00bae2',
}

interface ProgressBarProps {
  value: number
  max?: number
  accent?: keyof typeof accentColors
  label?: string
  className?: string
}

export function ProgressBar({ value, max = 100, accent = 'green', label, className = '' }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const color = accentColors[accent] || accentColors.green

  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <div className="text-xs mb-1.5" style={{ color: '#7c7c6f' }}>{label}</div>
      )}
      <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: '#242624' }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}
