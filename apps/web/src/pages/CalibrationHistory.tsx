import { useState, useEffect } from 'react'
import { fetchJson, listActionAlignmentScores, listWeeklyReviews } from '../api'
import type { ActionAlignmentScore, VerdictLabel, WeeklyReviewSession } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

const VERDICT_DESCRIPTIONS: Record<VerdictLabel, string> = {
  aligned_progress: 'Actions matched your stated direction. You did what you intended.',
  noisy_progress: 'You made progress, but not in your intended direction. Some drift.',
  avoidance_disguised_as_work: 'Activity looked productive but avoided the real problem.',
  recovery_week: 'You bounced back from a stall or setback. Restorative week.',
  unstable_but_useful: 'Inconsistent, but some meaningful progress happened.',
  blocked_by_environment: 'External factors prevented progress despite intention.',
}

const SCORE_EXPLANATION = 'Action alignment score (0.0-1.0) measures how well your actions matched your intended direction. Higher = better alignment. Verdict labels describe the pattern of your week.'

function formatScore(value: number): string {
  return value.toFixed(2)
}

function getTrend(scores: ActionAlignmentScore[]): 'up' | 'down' | 'stable' | 'first' {
  if (scores.length < 2) return 'first'
  const sorted = [...scores].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  const latest = sorted[sorted.length - 1].action_alignment_score
  const prev = sorted[sorted.length - 2].action_alignment_score
  const diff = latest - prev
  if (diff > 0.05) return 'up'
  if (diff < -0.05) return 'down'
  return 'stable'
}

function trendArrow(trend: 'up' | 'down' | 'stable' | 'first'): string {
  if (trend === 'up') return '↑ improving'
  if (trend === 'down') return '↓ declining'
  if (trend === 'stable') return '→ stable'
  return 'first score'
}

export default function CalibrationHistory() {
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [weeklyReviews, setWeeklyReviews] = useState<WeeklyReviewSession[]>([])
  const [actionScores, setActionScores] = useState<ActionAlignmentScore[]>([])
  const [error, setError] = useState('')
  const [selectedScore, setSelectedScore] = useState<ActionAlignmentScore | null>(null)

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

  if (error && !data) return <ErrorDisplay message={error} onRetry={() => { setError(''); window.location.reload() }} />
  if (!data) return <LoadingSpinner label="Loading calibration history..." />

  const records = (data.records as Record<string, unknown>[]) || []
  const drift = (data.drift_evidence as Record<string, unknown>[]) || []
  const sortedScores = [...actionScores].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  const trend = getTrend(actionScores)

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Calibration History</h2>

      <div className="p-3 mb-4 bg-blue-950/30 rounded-lg border border-blue-800/30">
        <h4 className="text-sm font-medium mb-1">What does this page show?</h4>
        <p className="text-sm text-gray-300">{SCORE_EXPLANATION}</p>
        <p className="text-xs text-gray-400 mt-1">
          <strong>Weekly reviews</strong> are sessions where you reflect on your week.
          <strong> Action alignment scores</strong> measure how well your actions matched your intentions.
          <strong> Calibration records</strong> are the raw score data.
        </p>
      </div>

      <h3 className="text-base font-medium">Weekly Reviews ({weeklyReviews.length})</h3>
      {weeklyReviews.length === 0 && <p className="text-gray-400 text-sm">No weekly reviews yet.</p>}
      {weeklyReviews.map(session => (
        <div key={session.session_id} className="p-2 bg-gray-800/50 rounded text-sm">
          <strong>{session.session_id}</strong> — {session.status}<br />
          Note: {session.weekly_note_record_id}<br />
          {session.created_at && <span className="text-xs text-gray-500">Created: {session.created_at}</span>}<br />
          Next correction: {session.next_week_primary_correction || 'pending'}
        </div>
      ))}

      <h3 className="text-base font-medium">Action Alignment ({actionScores.length}) {trendArrow(trend)}</h3>
      {actionScores.length === 0 && <p className="text-gray-400 text-sm">No action alignment records yet.</p>}
      {sortedScores.map(score => (
        <div
          key={score.score_id}
          className={`p-2 rounded cursor-pointer text-sm transition-colors ${
            selectedScore?.score_id === score.score_id
              ? 'bg-green-950/40 border border-green-700/50'
              : 'bg-gray-800/30 border border-transparent hover:bg-gray-800/50'
          }`}
          onClick={() => setSelectedScore(selectedScore?.score_id === score.score_id ? null : score)}
        >
          <strong>{score.score_id}</strong> — {formatScore(score.action_alignment_score)}<br />
          Verdict: {score.verdict_label.replace(/_/g, ' ')}<br />
          {score.created_at && <span className="text-xs text-gray-500">{score.created_at}</span>}

          {selectedScore?.score_id === score.score_id && (
            <div className="mt-2 p-3 bg-gray-800 rounded border border-gray-700">
              <h4 className="text-sm font-medium mb-2">Score Detail</h4>
              <p className="text-sm"><strong>Score:</strong> {formatScore(score.action_alignment_score)} (0.0 = no alignment, 1.0 = full alignment)</p>
              <p className="text-sm"><strong>Verdict:</strong> {VERDICT_DESCRIPTIONS[score.verdict_label] || score.verdict_label}</p>
              <p className="text-sm"><strong>Your words:</strong> {score.verdict_sentence || '(none)'}</p>
              <p className="text-sm mt-1"><strong>Dimensions:</strong></p>
              <ul className="list-disc list-inside text-sm text-gray-300 ml-2">
                <li>Direction alignment: {formatScore(score.scores.direction_alignment)}</li>
                <li>Execution consistency: {formatScore(score.scores.execution_consistency)}</li>
                <li>Avoidance level: {formatScore(score.scores.avoidance_level)}</li>
              </ul>
              <p className="text-sm mt-1"><strong>Evidence:</strong></p>
              <ul className="list-disc list-inside text-sm text-gray-300 ml-2">
                <li>Action: {score.evidence.one_action_evidence || '(none)'}</li>
                <li>Avoidance: {score.evidence.one_avoidance_or_friction_evidence || '(none)'}</li>
                <li>Next correction: {score.evidence.one_next_correction || '(none)'}</li>
              </ul>
              <p className="text-xs text-gray-500 mt-2">Session: {score.session_id}</p>
            </div>
          )}
        </div>
      ))}

      <h3 className="text-base font-medium">Scores ({String(data.count)})</h3>
      {records.length === 0 && <p className="text-gray-400 text-sm">No scores yet.</p>}
      {records.map(r => (
        <div key={String(r.id)} className="p-2 bg-gray-800/30 rounded text-sm">
          <strong>{String(r.id)}</strong> — {String(r.alter_id)}<br />
          Actual: {JSON.stringify(r.actual_scores)}
        </div>
      ))}
      {drift.length > 0 && (
        <>
          <h3 className="text-base font-medium">Drift Evidence</h3>
          {drift.map((d, i) => (
            <div key={i} className="p-2 bg-red-950/30 border border-red-800/30 rounded text-sm">
              Overall: {String(d.overall)} | Threshold exceeded: {String(d.threshold_exceeded)}
            </div>
          ))}
        </>
      )}
    </div>
  )
}
