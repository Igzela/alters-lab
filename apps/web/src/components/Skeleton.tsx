import { useTranslation } from 'react-i18next'

interface SkeletonProps {
  lines?: number
  className?: string
}

export function Skeleton({ lines = 3, className = '' }: SkeletonProps) {
  const { t } = useTranslation()
  return (
    <div className={`space-y-2 ${className}`} role="status" aria-label={t('common.loading')}>
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          className="skeleton-shimmer rounded-lg"
          style={{
            height: '14px',
            width: i === lines - 1 ? '60%' : '100%',
          }}
        />
      ))}
      <span className="sr-only">{t('common.loading')}</span>
    </div>
  )
}

export function SkeletonCard({ className = '' }: { className?: string }) {
  const { t } = useTranslation()
  return (
    <div
      className={`p-4 rounded-xl skeleton-shimmer ${className}`}
      style={{ backgroundColor: '#ffffff', border: '1px solid #e8e6e1' }}
      role="status"
      aria-label={t('common.loading')}
    >
      <div className="space-y-2">
        <div style={{ height: '14px', width: '40%', backgroundColor: '#e8e6e1', borderRadius: '6px' }} />
        <div style={{ height: '12px', width: '80%', backgroundColor: '#e8e6e1', borderRadius: '6px' }} />
        <div style={{ height: '12px', width: '60%', backgroundColor: '#e8e6e1', borderRadius: '6px' }} />
      </div>
      <span className="sr-only">{t('common.loading')}</span>
    </div>
  )
}
