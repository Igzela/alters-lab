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

  const weekApprox = counts ? Math.min(4, Math.max(counts.weeklyReviews, counts.actionAlignment)) : 0

  return (
    <section style={panelStyle}>
      <h3 style={{ marginTop: 0 }}>P6 Progress</h3>
      {error && <p style={{ color: '#b00020' }}>Progress unavailable: {error}</p>}
      {!counts && !error && <p>Loading progress...</p>}
      {counts && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10 }}>
            <div><strong>{counts.weeklyNotes}</strong><br />weekly notes</div>
            <div><strong>{counts.weeklyReviews}</strong><br />weekly reviews</div>
            <div><strong>{counts.actionAlignment}</strong><br />action alignment records</div>
            <div><strong>Week {weekApprox}/4</strong><br />approximate evidence progress</div>
          </div>
          <h4>Missing requirements</h4>
          <ul>
            <li>4 real weekly reviews: {Math.min(counts.weeklyReviews, 4)}/4</li>
            <li>4 calibration records: {Math.min(counts.actionAlignment, 4)}/4</li>
            <li>1 pattern review: not tracked here</li>
            <li>4-week evidence window: not validated</li>
          </ul>
        </>
      )}
      <p>P6 behavior validated: false</p>
      <p>P6 sealed: false</p>
    </section>
  )
}
