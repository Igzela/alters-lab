import { useTranslation } from 'react-i18next'
import { X } from '@phosphor-icons/react'
import { fadeIn } from '../animations'
import { useEffect, useRef } from 'react'

interface ShortcutHelpProps {
  onClose: () => void
}

const shortcuts = [
  { key: 'D', label: 'nav.dashboard' },
  { key: 'S', label: 'nav.status' },
  { key: 'W', label: 'nav.weeklyReview' },
  { key: 'R', label: 'nav.realityScore' },
  { key: 'H', label: 'nav.history' },
  { key: 'P', label: 'nav.patterns' },
  { key: 'C', label: 'nav.checkpointPlan' },
  { key: 'A', label: 'nav.dialogue' },
  { key: 'V', label: 'nav.validation' },
  { key: 'T', label: 'nav.provider' },
]

export default function ShortcutHelp({ onClose }: ShortcutHelpProps) {
  const { t } = useTranslation()
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (ref.current) fadeIn(ref.current, 0.15)
  }, [])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
      onClick={onClose}
    >
      <div
        ref={ref}
        className="w-full max-w-md rounded-xl p-6 shadow-xl"
        style={{ backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text)' }}>
            {t('shortcuts.title')}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg transition-colors duration-150 border-none cursor-pointer"
            style={{ color: 'var(--color-text-muted)', backgroundColor: 'transparent' }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-medium" style={{ color: 'var(--color-text-secondary)' }}>
            {t('shortcuts.pressGThen')}
          </p>
          <div className="grid grid-cols-2 gap-2">
            {shortcuts.map(s => (
              <div key={s.key} className="flex items-center gap-2">
                <kbd
                  className="inline-flex items-center justify-center w-7 h-7 rounded text-xs font-mono font-medium"
                  style={{ backgroundColor: 'var(--color-surface-raised)', color: 'var(--color-text)', border: '1px solid var(--color-border)' }}
                >
                  {s.key}
                </kbd>
                <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                  {t(s.label)}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2 border-t" style={{ borderColor: 'var(--color-border)' }}>
            <div className="flex items-center gap-2">
              <kbd
                className="inline-flex items-center justify-center w-7 h-7 rounded text-xs font-mono font-medium"
                style={{ backgroundColor: 'var(--color-surface-raised)', color: 'var(--color-text)', border: '1px solid var(--color-border)' }}
              >
                ?
              </kbd>
              <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                {t('shortcuts.showHelp')}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
