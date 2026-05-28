import { useState, useEffect, useCallback, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson, postJson } from '../api'
import { staggerFadeIn } from '../animations'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Banner } from '../components/Banner'
import LoadingSpinner from '../components/LoadingSpinner'
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
  const { t } = useTranslation()
  const [reviews, setReviews] = useState<PatternReviewRecord[]>([])
  const [selected, setSelected] = useState<PatternReviewRecord | null>(null)
  const [building, setBuilding] = useState(false)
  const [loadingList, setLoadingList] = useState(true)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const cardsRef = useRef<HTMLDivElement>(null)

  const loadList = useCallback(() => {
    setLoadingList(true)
    setError('')
    fetchJson('/pattern-review/list')
      .then(res => {
        const sorted = [...res.reviews].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        setReviews(sorted)
      })
      .catch(e => setError(e instanceof Error ? e.message : t('patterns.unableToLoad')))
      .finally(() => setLoadingList(false))
  }, [t])

  useEffect(() => { loadList() }, [])

  useEffect(() => {
    if (!loadingList && cardsRef.current) {
      const cards = cardsRef.current.querySelectorAll('[data-stagger]')
      staggerFadeIn(Array.from(cards) as HTMLElement[])
    }
  }, [loadingList, reviews])

  const buildReview = async () => {
    setBuilding(true)
    setError('')
    setStatus('')
    try {
      const res = await postJson('/pattern-review/build', { weekly_patterns: [], save: true, caller: 'api' })
      setStatus(`${t('patterns.reviewBuilt')}: ${res.review.review_id}`)
      setSelected(res.review)
      loadList()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('patterns.buildFailed'))
    } finally {
      setBuilding(false)
    }
  }

  const loadDetail = (reviewId: string) => {
    setError('')
    setLoadingDetail(true)
    fetchJson(`/pattern-review/${reviewId}`)
      .then(res => setSelected(res.review))
      .catch(e => setError(e instanceof Error ? e.message : t('patterns.unableToLoadReview')))
      .finally(() => setLoadingDetail(false))
  }

  return (
    <div ref={cardsRef} className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('patterns.title')}</h2>
      <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('patterns.description')}</p>

      <Banner variant="warning">{t('patterns.boundaryCopy')}</Banner>

      <div className="flex items-center gap-3 mb-4">
        <Button variant="primary" accent="orange" onClick={buildReview} disabled={building}>
          {building ? t('patterns.building') : t('patterns.buildNew')}
        </Button>
        {status && <span className="text-sm" style={{ color: '#0ae448' }}>{status}</span>}
        {error && <span className="text-sm" style={{ color: '#ff4444' }}>{error}</span>}
      </div>

      {loadingList && <LoadingSpinner label={t('patterns.loadingReviews')} />}

      {!loadingList && reviews.length === 0 && !error && (
        <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('patterns.noReviews')}</p>
      )}

      {reviews.map(r => (
        <div
          key={r.review_id}
          data-stagger
          onClick={() => loadDetail(r.review_id)}
          className="p-3 rounded-xl cursor-pointer transition-all duration-200"
          style={{
            backgroundColor: selected?.review_id === r.review_id ? '#242624' : '#1a1c1a',
            border: selected?.review_id === r.review_id ? '2px solid #ff8709' : '1px solid #242624',
          }}
        >
          <div className="flex justify-between items-center">
            <strong className="text-sm">{r.review_id}</strong>
            <Badge variant={STATUS_BADGE[r.status] || 'muted'}>{r.status.replace(/_/g, ' ')}</Badge>
          </div>
          <div className="text-xs mt-1" style={{ color: '#7c7c6f' }}>
            {t('patterns.weeksEvaluated')} {r.weeks_evaluated} | {t('patterns.patternsTriggered')} {r.triggered_patterns.length}
            {r.created_at && <span className="ml-2">{r.created_at}</span>}
          </div>
        </div>
      ))}

      {loadingDetail && <LoadingSpinner label={t('patterns.loadingDetail')} />}

      {selected && !loadingDetail && (
        <Card accent="orange">
          <h3 className="text-sm font-medium mb-2">{t('patterns.reviewDetail')} {selected.review_id}</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 mb-3 text-sm">
            <div><strong>{selected.weeks_evaluated}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('patterns.weeksEvaluated')}</span></div>
            <div><strong>{selected.triggered_patterns.length}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('patterns.patternsTriggered')}</span></div>
            <div>
              <Badge variant={STATUS_BADGE[selected.status] || 'muted'}>{selected.status.replace(/_/g, ' ')}</Badge>
            </div>
          </div>

          {selected.triggered_patterns.length > 0 ? (
            <div>
              <h4 className="text-sm font-medium mb-2">{t('patterns.triggeredPatterns')}</h4>
              {selected.triggered_patterns.map((tp, i) => (
                <div key={i} className="p-2 mb-1.5 rounded-lg text-sm" style={{ backgroundColor: '#1a1c1a', border: '1px solid #242624' }}>
                  <strong>{PATTERN_LABELS[tp.pattern] || tp.pattern}</strong>
                  <div className="text-xs mt-1" style={{ color: '#7c7c6f' }}>
                    {t('patterns.occurrences')} {tp.occurrences} | {t('patterns.confidence')} {(tp.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs mt-0.5" style={{ color: '#7c7c6f' }}>
                    {t('patterns.strategy')} {tp.strategy_constraint}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('patterns.noPatterns')}</p>
          )}
        </Card>
      )}
    </div>
  )
}
