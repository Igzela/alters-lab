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
    <div ref={ref} className="p-3 rounded-lg text-sm flex items-start gap-2" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626' }}>
      <span className="flex-1">{message}</span>
      {onRetry && (
        <button
          className="text-xs underline shrink-0 cursor-pointer border-none bg-transparent transition-colors"
          style={{ color: '#dc2626' }}
          onClick={onRetry}
        >
          {t('loading.retry')}
        </button>
      )}
    </div>
  )
}
