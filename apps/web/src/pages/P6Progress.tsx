import { useEffect, useState } from 'react'
import { listActionAlignmentScores, listWeeklyNotes, listWeeklyReviews } from '../api'

type Counts = {
  weeklyNotes: number
  weeklyReviews: number
  actionAlignment: number
}

const panelStyle = {
  border: '1px solid #ddd',
  borderRadius: 6,
  padding: 14,
  marginBottom: 18,
  background: '#fbfbfb',
}

export default function P6Progress() {
  const [counts, setCounts] = useState<Counts | null>(null)
  const [error, setError] = useState('')

  const load = () => {
    Promise.all([listWeeklyNotes(), listWeeklyReviews(), listActionAlignmentScores()])
      .then(([notes, reviews, scores]) => {
        setCounts({
          weeklyNotes: notes.count,
          weeklyReviews: reviews.count,
          actionAlignment: scores.count,
        })
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Unable to load P6 progress'))
  }

  useEffect(() => {
    load()
  }, [])

  const weeksComplete = counts ? Math.min(4, counts.weeklyReviews) : 0
  const scoresComplete = counts ? Math.min(4, counts.actionAlignment) : 0

  return (
    <section style={panelStyle}>
      <h3 style={{ marginTop: 0 }}>Your Progress</h3>
      {error && <p style={{ color: '#b00020' }}>Progress unavailable: {error}</p>}
      {!counts && !error && <p>Loading progress...</p>}
      {counts && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10 }}>
            <div><strong>{counts.weeklyNotes}</strong><br />weekly notes ingested</div>
            <div><strong>{counts.weeklyReviews}</strong><br />weekly reviews completed</div>
            <div><strong>{counts.actionAlignment}</strong><br />alignment scores recorded</div>
          </div>

          <div style={{ marginTop: 14, padding: 12, background: '#fff', borderRadius: 4, border: '1px solid #e0e0e0' }}>
            <h4 style={{ margin: '0 0 8px' }}>Validation Status</h4>
            <p style={{ margin: '0 0 6px', fontSize: 14 }}>
              <strong>Not started.</strong> P6 validation requires 4 weekly reviews and 4 calibration records across 21+ days.
            </p>
            <p style={{ margin: 0, fontSize: 13, color: '#666' }}>
              Weekly reviews: {weeksComplete}/4 | Alignment scores: {scoresComplete}/4 | 4-week window: not yet met
            </p>
          </div>

          <div style={{ marginTop: 10, fontSize: 13, color: '#555' }}>
            <strong>Next step:</strong> Continue weekly reviews as pilot evidence; P6 validation start remains blocked until product completeness closeout.
          </div>
        </>
      )}
      <p style={{ fontSize: 12, color: '#999', marginTop: 10 }}>P6 behavior validated: false | P6 sealed: false</p>
    </section>
  )
}
