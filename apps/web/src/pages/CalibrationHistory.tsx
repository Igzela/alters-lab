import { useState, useEffect } from 'react'
import { fetchJson, listActionAlignmentScores, listWeeklyReviews } from '../api'
import type { ActionAlignmentScore, WeeklyReviewSession } from '../types'

export default function CalibrationHistory() {
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [weeklyReviews, setWeeklyReviews] = useState<WeeklyReviewSession[]>([])
  const [actionScores, setActionScores] = useState<ActionAlignmentScore[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      fetchJson('/calibration-loop/history'),
      listWeeklyReviews(),
      listActionAlignmentScores(),
    ])
      .then(([history, reviews, scores]) => {
        setData(history)
        setWeeklyReviews(reviews.sessions)
        setActionScores(scores.scores)
      })
      .catch(e => setError(e.message))
  }, [])

  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>
  if (!data) return <p>Loading...</p>

  const records = (data.records as Record<string, unknown>[]) || []
  const drift = (data.drift_evidence as Record<string, unknown>[]) || []

  return (
    <div>
      <h2>Calibration History</h2>
      <p>Weekly review records and action alignment records created from the Weekly Review page appear in local runtime storage.</p>
      <p>Read-only: {data.read_only ? 'Yes' : 'No'}</p>
      <h3>Weekly Reviews ({weeklyReviews.length})</h3>
      {weeklyReviews.length === 0 && <p>No weekly reviews yet.</p>}
      {weeklyReviews.map(session => (
        <div key={session.session_id} style={{ padding: 8, marginBottom: 8, background: '#f6f8ff' }}>
          <strong>{session.session_id}</strong> — {session.status}<br />
          Note: {session.weekly_note_record_id}<br />
          Next correction: {session.next_week_primary_correction || 'pending'}
        </div>
      ))}
      <h3>Action Alignment ({actionScores.length})</h3>
      {actionScores.length === 0 && <p>No action alignment records yet.</p>}
      {actionScores.map(score => (
        <div key={score.score_id} style={{ padding: 8, marginBottom: 8, background: '#f8fff6' }}>
          <strong>{score.score_id}</strong> — {score.action_alignment_score}<br />
          Verdict: {score.verdict_label}
        </div>
      ))}
      <h3>Scores ({String(data.count)})</h3>
      {records.length === 0 && <p>No scores yet.</p>}
      {records.map(r => (
        <div key={String(r.id)} style={{ padding: 8, marginBottom: 8, background: '#f9f9f9' }}>
          <strong>{String(r.id)}</strong> — {String(r.alter_id)}<br />
          Actual: {JSON.stringify(r.actual_scores)}
        </div>
      ))}
      {drift.length > 0 && (
        <>
          <h3>Drift Evidence</h3>
          {drift.map((d, i) => (
            <div key={i} style={{ padding: 8, marginBottom: 8, background: '#fff3f3' }}>
              Overall: {String(d.overall)} | Threshold exceeded: {String(d.threshold_exceeded)}
            </div>
          ))}
        </>
      )}
    </div>
  )
}
