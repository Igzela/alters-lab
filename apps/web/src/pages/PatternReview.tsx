import { useState, useEffect } from 'react'
import { fetchJson, postJson } from '../api'

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
  const [reviews, setReviews] = useState<PatternReviewRecord[]>([])
  const [selected, setSelected] = useState<PatternReviewRecord | null>(null)
  const [building, setBuilding] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  const loadList = () => {
    fetchJson('/pattern-review/list')
      .then(res => {
        const sorted = [...res.reviews].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        setReviews(sorted)
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Unable to load pattern reviews'))
  }

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
      setError(e instanceof Error ? e.message : 'Build failed')
    } finally {
      setBuilding(false)
    }
  }

  const loadDetail = (reviewId: string) => {
    setError('')
    fetchJson(`/pattern-review/${reviewId}`)
      .then(res => setSelected(res.review))
      .catch(e => setError(e instanceof Error ? e.message : 'Unable to load review'))
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Pattern Review</h2>
      <p className="text-gray-500 text-xs">
        Detects repeated behavioral patterns across weekly reviews. Patterns indicate recurring tendencies that may need attention.
      </p>
      <div className="p-2.5 bg-amber-950/30 border border-amber-800/50 rounded-lg mb-4 text-xs text-amber-200">
        Pattern review is supporting evidence only. It does not validate or seal P6. Provider output is not counted as evidence. P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED.
      </div>

      <div className="mb-4">
        <button
          className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50"
          onClick={buildReview}
          disabled={building}
        >
          {building ? 'Building...' : 'Build New Pattern Review'}
        </button>
        {status && <span className="text-green-400 text-sm ml-2">{status}</span>}
        {error && <span className="text-red-500 text-sm ml-2">{error}</span>}
      </div>

      {reviews.length === 0 && <p className="text-gray-400 text-sm">No pattern reviews yet. Build one to get started.</p>}

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
            Weeks evaluated: {r.weeks_evaluated} | Patterns triggered: {r.triggered_patterns.length}
            {r.created_at && <span className="ml-2">{r.created_at}</span>}
          </div>
        </div>
      ))}

      {selected && (
        <div className="mt-4 p-3.5 bg-blue-950/30 rounded-lg border border-blue-800/30">
          <h3 className="text-sm font-medium mb-2">Review Detail: {selected.review_id}</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 mb-3 text-sm">
            <div><strong>{selected.weeks_evaluated}</strong><br /><span className="text-gray-400 text-xs">weeks evaluated</span></div>
            <div><strong>{selected.triggered_patterns.length}</strong><br /><span className="text-gray-400 text-xs">patterns triggered</span></div>
            <div>
              <strong className={STATUS_COLORS[selected.status] || 'text-gray-400'}>{selected.status.replace(/_/g, ' ')}</strong>
            </div>
          </div>

          {selected.triggered_patterns.length > 0 ? (
            <div>
              <h4 className="text-sm font-medium mb-2">Triggered Patterns</h4>
              {selected.triggered_patterns.map((tp, i) => (
                <div key={i} className="p-2 mb-1.5 bg-gray-800/50 rounded border border-gray-700 text-sm">
                  <strong>{PATTERN_LABELS[tp.pattern] || tp.pattern}</strong>
                  <div className="text-xs text-gray-400 mt-1">
                    Occurrences: {tp.occurrences} | Confidence: {(tp.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    Strategy: {tp.strategy_constraint}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No patterns triggered in this review.</p>
          )}
        </div>
      )}
    </div>
  )
}
