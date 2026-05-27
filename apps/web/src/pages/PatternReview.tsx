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
  insufficient_data: '#888',
  no_pattern: '#4caf50',
  pattern_triggered: '#e65100',
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
      const res = await postJson('/pattern-review/build', {
        weekly_patterns: [],
        save: true,
        caller: 'api',
      })
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
    <div>
      <h2>Pattern Review</h2>
      <p style={{ color: '#888', fontSize: 12 }}>
        Detects repeated behavioral patterns across weekly reviews. Patterns indicate recurring tendencies that may need attention.
      </p>

      <div style={{ marginBottom: 16 }}>
        <button onClick={buildReview} disabled={building}>
          {building ? 'Building...' : 'Build New Pattern Review'}
        </button>
        {status && <span style={{ color: 'green', marginLeft: 8 }}>{status}</span>}
        {error && <span style={{ color: 'red', marginLeft: 8 }}>{error}</span>}
      </div>

      {reviews.length === 0 && <p style={{ color: '#888' }}>No pattern reviews yet. Build one to get started.</p>}

      {reviews.map(r => (
        <div
          key={r.review_id}
          onClick={() => loadDetail(r.review_id)}
          style={{
            padding: 10,
            marginBottom: 8,
            border: selected?.review_id === r.review_id ? '2px solid #333' : '1px solid #ddd',
            borderRadius: 6,
            cursor: 'pointer',
            background: '#fafafa',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>{r.review_id}</strong>
            <span style={{ color: STATUS_COLORS[r.status] || '#888', fontSize: 13 }}>{r.status.replace(/_/g, ' ')}</span>
          </div>
          <div style={{ fontSize: 13, color: '#666', marginTop: 4 }}>
            Weeks evaluated: {r.weeks_evaluated} | Patterns triggered: {r.triggered_patterns.length}
            {r.created_at && <span style={{ marginLeft: 8 }}>{r.created_at}</span>}
          </div>
        </div>
      ))}

      {selected && (
        <div style={{ marginTop: 16, padding: 14, background: '#f6f8ff', borderRadius: 6, border: '1px solid #d0daf0' }}>
          <h3 style={{ margin: '0 0 10px' }}>Review Detail: {selected.review_id}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, marginBottom: 12 }}>
            <div><strong>{selected.weeks_evaluated}</strong><br />weeks evaluated</div>
            <div><strong>{selected.triggered_patterns.length}</strong><br />patterns triggered</div>
            <div>
              <strong style={{ color: STATUS_COLORS[selected.status] || '#888' }}>{selected.status.replace(/_/g, ' ')}</strong>
            </div>
          </div>

          {selected.triggered_patterns.length > 0 ? (
            <div>
              <h4 style={{ margin: '0 0 8px' }}>Triggered Patterns</h4>
              {selected.triggered_patterns.map((tp, i) => (
                <div key={i} style={{ padding: 8, marginBottom: 6, background: '#fff', borderRadius: 4, border: '1px solid #e0e0e0' }}>
                  <strong>{PATTERN_LABELS[tp.pattern] || tp.pattern}</strong>
                  <div style={{ fontSize: 13, color: '#666', marginTop: 4 }}>
                    Occurrences: {tp.occurrences} | Confidence: {(tp.confidence * 100).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: 12, color: '#888', marginTop: 2 }}>
                    Strategy: {tp.strategy_constraint}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#888' }}>No patterns triggered in this review.</p>
          )}
        </div>
      )}
    </div>
  )
}
