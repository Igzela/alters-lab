import { useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { fadeIn, shakeError } from '../animations'

interface ErrorDisplayProps {
  message: string
  onRetry?: () => void
}

export default function ErrorDisplay({ message, onRetry }: ErrorDisplayProps) {
  const { t } = useTranslation()
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (ref.current) {
      fadeIn(ref.current)
      shakeError(ref.current)
    }
  }, [message])

  return (
    <div ref={ref} className="p-3 rounded-lg text-sm flex items-start gap-2" style={{ backgroundColor: 'var(--color-error-light)', border: '1px solid color-mix(in srgb, var(--color-error) 25%, var(--color-error-light))', color: 'var(--color-error)' }}>
      <span className="flex-1">{message}</span>
      {onRetry && (
        <button
          className="text-xs underline shrink-0 cursor-pointer border-none bg-transparent transition-colors"
          style={{ color: 'var(--color-error)' }}
          onClick={onRetry}
        >
          {t('loading.retry')}
        </button>
      )}
    </div>
  )
}
