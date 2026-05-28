import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson, postJson } from '../api'
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

const STATUS_COLORS: Record<string, string> = {
  insufficient_data: 'text-gray-400',
  no_pattern: 'text-green-400',
  pattern_triggered: 'text-orange-400',
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

  const buildReview = async () => {
    setBuilding(true)
    setError('')
    setStatus('')
    try {
      const res = await postJson('/pattern-review/build', { weekly_patterns: [], save: true, caller: 'api' })
      setStatus(`Review built: ${res.review.review_id}`)
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
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{t('patterns.title')}</h2>
      <p className="text-gray-500 text-xs">
        {t('patterns.description')}
      </p>
      <div className="p-2.5 bg-amber-950/30 border border-amber-800/50 rounded-lg mb-4 text-xs text-amber-200">
        {t('patterns.boundaryCopy')}
      </div>

      <div className="mb-4">
        <button
          className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50"
          onClick={buildReview}
          disabled={building}
        >
          {building ? t('patterns.building') : t('patterns.buildNew')}
        </button>
        {status && <span className="text-green-400 text-sm ml-2">{status}</span>}
        {error && <span className="text-red-500 text-sm ml-2">{error}</span>}
      </div>

      {loadingList && <LoadingSpinner label={t('patterns.loadingReviews')} />}

      {!loadingList && reviews.length === 0 && !error && <p className="text-gray-400 text-sm">{t('patterns.noReviews')}</p>}

      {reviews.map(r => (
        <div
          key={r.review_id}
          onClick={() => loadDetail(r.review_id)}
          className={`p-2.5 rounded-lg cursor-pointer transition-colors ${
            selected?.review_id === r.review_id
              ? 'border-2 border-gray-600 bg-gray-800/50'
              : 'border border-gray-700 hover:bg-gray-800/30'
          }`}
        >
          <div className="flex justify-between items-center">
            <strong className="text-sm">{r.review_id}</strong>
            <span className={`text-xs ${STATUS_COLORS[r.status] || 'text-gray-400'}`}>{r.status.replace(/_/g, ' ')}</span>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {t('patterns.weeksEvaluated')} {r.weeks_evaluated} | {t('patterns.patternsTriggered')} {r.triggered_patterns.length}
            {r.created_at && <span className="ml-2">{r.created_at}</span>}
          </div>
        </div>
      ))}

      {loadingDetail && <LoadingSpinner label={t('patterns.loadingDetail')} />}

      {selected && !loadingDetail && (
        <div className="mt-4 p-3.5 bg-blue-950/30 rounded-lg border border-blue-800/30">
          <h3 className="text-sm font-medium mb-2">{t('patterns.reviewDetail')} {selected.review_id}</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 mb-3 text-sm">
            <div><strong>{selected.weeks_evaluated}</strong><br /><span className="text-gray-400 text-xs">{t('patterns.weeksEvaluated')}</span></div>
            <div><strong>{selected.triggered_patterns.length}</strong><br /><span className="text-gray-400 text-xs">{t('patterns.patternsTriggered')}</span></div>
            <div>
              <strong className={STATUS_COLORS[selected.status] || 'text-gray-400'}>{selected.status.replace(/_/g, ' ')}</strong>
            </div>
          </div>

          {selected.triggered_patterns.length > 0 ? (
            <div>
              <h4 className="text-sm font-medium mb-2">{t('patterns.triggeredPatterns')}</h4>
              {selected.triggered_patterns.map((tp, i) => (
                <div key={i} className="p-2 mb-1.5 bg-gray-800/50 rounded border border-gray-700 text-sm">
                  <strong>{PATTERN_LABELS[tp.pattern] || tp.pattern}</strong>
                  <div className="text-xs text-gray-400 mt-1">
                    {t('patterns.occurrences')} {tp.occurrences} | {t('patterns.confidence')} {(tp.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {t('patterns.strategy')} {tp.strategy_constraint}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">{t('patterns.noPatterns')}</p>
          )}
        </div>
      )}
    </div>
  )
}
