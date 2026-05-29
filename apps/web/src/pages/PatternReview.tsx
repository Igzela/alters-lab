import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { usePatternReviews, useBuildPatternReview, usePatternReviewDetail } from '../hooks/useApi'
import { staggerFadeIn } from '../animations'
import { formatDate } from '../dateFormat'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Banner } from '../components/Banner'
import { Skeleton } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'

interface TriggeredPattern {
  pattern: string
  occurrences: number
  confidence: number
  strategy_constraint: string
}

interface PatternReviewRecord {
  review_id: string
  status: string
  weeks_evaluated: number
  triggered_patterns: TriggeredPattern[]
  created_at: string
}

const PATTERN_LABELS: Record<string, string> = {
  repeated_noisy_progress: 'Noisy Progress',
  repeated_avoidance_disguised_as_work: 'Avoidance Disguised as Work',
  repeated_sleep_breakdown: 'Sleep Breakdown',
  repeated_over_scope: 'Over Scope',
  repeated_action_mismatch: 'Action Mismatch',
  repeated_primary_correction_failure: 'Correction Failure',
}

const STATUS_BADGE: Record<string, 'muted' | 'success' | 'warning'> = {
  insufficient_data: 'muted',
  no_pattern: 'success',
  pattern_triggered: 'warning',
}

export default function PatternReview() {
  const { t, i18n } = useTranslation()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [status, setStatus] = useState('')
  const cardsRef = useRef<HTMLDivElement>(null)

  const reviewsQuery = usePatternReviews()
  const buildMutation = useBuildPatternReview()
  const detailQuery = usePatternReviewDetail(selectedId)

  const reviews: PatternReviewRecord[] = reviewsQuery.data
    ? [...(reviewsQuery.data.reviews || [])].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    : []

  const selected: PatternReviewRecord | null = detailQuery.data?.review || null

  useEffect(() => {
    if (!reviewsQuery.isLoading && cardsRef.current) {
      const cards = cardsRef.current.querySelectorAll('[data-stagger]')
      staggerFadeIn(Array.from(cards) as HTMLElement[])
    }
  }, [reviewsQuery.isLoading, reviews])

  const buildReview = () => {
    setStatus('')
    buildMutation.mutate(
      { weekly_patterns: [], save: true, caller: 'api' },
      {
        onSuccess: (res) => {
          const review = (res as Record<string, unknown>).review as Record<string, unknown> | undefined
          setStatus(`${t('patterns.reviewBuilt')}: ${review?.review_id || ''}`)
          setSelectedId(review?.review_id as string || null)
          reviewsQuery.refetch()
        },
      }
    )
  }

  const error = reviewsQuery.error || buildMutation.error

  return (
    <div ref={cardsRef} className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('patterns.title')}</h2>
      <p className="text-sm" style={{ color: '#78716c' }}>{t('patterns.description')}</p>

      <Banner variant="warning">{t('patterns.boundaryCopy')}</Banner>

      <div className="flex items-center gap-3 mb-4">
        <Button variant="primary" onClick={buildReview} disabled={buildMutation.isPending}>
          {buildMutation.isPending ? t('patterns.building') : t('patterns.buildNew')}
        </Button>
        {status && <span className="text-sm" style={{ color: '#16a34a' }}>{status}</span>}
        {error && <span className="text-sm" style={{ color: '#dc2626' }}>{(error as Error).message}</span>}
      </div>

      {reviewsQuery.isLoading && <Skeleton lines={4} />}

      {!reviewsQuery.isLoading && reviews.length === 0 && !error && (
        <p className="text-sm" style={{ color: '#a8a29e' }}>{t('patterns.noReviews')}</p>
      )}

      {reviews.map(r => (
        <div
          key={r.review_id}
          data-stagger
          onClick={() => setSelectedId(selectedId === r.review_id ? null : r.review_id)}
          className="p-3 rounded-xl cursor-pointer transition-all duration-200"
          style={{
            backgroundColor: selectedId === r.review_id ? '#f5f4f0' : '#ffffff',
            border: selectedId === r.review_id ? '2px solid #b45309' : '1px solid #e8e6e1',
          }}
        >
          <div className="flex justify-between items-center">
            <strong className="text-sm">{r.review_id}</strong>
            <Badge variant={STATUS_BADGE[r.status] || 'muted'}>{r.status.replace(/_/g, ' ')}</Badge>
          </div>
          <div className="text-xs mt-1" style={{ color: '#a8a29e' }}>
            {t('patterns.weeksEvaluated')} {r.weeks_evaluated} | {t('patterns.patternsTriggered')} {r.triggered_patterns.length}
            {r.created_at && <span className="ml-2">{formatDate(r.created_at, i18n.language)}</span>}
          </div>
        </div>
      ))}

      {detailQuery.isLoading && <Skeleton lines={3} />}

      {selected && !detailQuery.isLoading && (
        <Card accent="amber">
          <h3 className="text-sm font-medium mb-2">{t('patterns.reviewDetail')} {selected.review_id}</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 mb-3 text-sm">
            <div><strong>{selected.weeks_evaluated}</strong><br /><span className="text-xs" style={{ color: '#a8a29e' }}>{t('patterns.weeksEvaluated')}</span></div>
            <div><strong>{selected.triggered_patterns.length}</strong><br /><span className="text-xs" style={{ color: '#a8a29e' }}>{t('patterns.patternsTriggered')}</span></div>
            <div>
              <Badge variant={STATUS_BADGE[selected.status] || 'muted'}>{selected.status.replace(/_/g, ' ')}</Badge>
            </div>
          </div>

          {selected.triggered_patterns.length > 0 ? (
            <div>
              <h4 className="text-sm font-medium mb-2">{t('patterns.triggeredPatterns')}</h4>
              {selected.triggered_patterns.map((tp, i) => (
                <div key={i} className="p-2 mb-1.5 rounded-lg text-sm" style={{ backgroundColor: '#faf9f7', border: '1px solid #e8e6e1' }}>
                  <strong>{PATTERN_LABELS[tp.pattern] || tp.pattern}</strong>
                  <div className="text-xs mt-1" style={{ color: '#a8a29e' }}>
                    {t('patterns.occurrences')} {tp.occurrences} | {t('patterns.confidence')} {(tp.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs mt-0.5" style={{ color: '#a8a29e' }}>
                    {t('patterns.strategy')} {tp.strategy_constraint}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: '#a8a29e' }}>{t('patterns.noPatterns')}</p>
          )}
        </Card>
      )}
    </div>
  )
}
