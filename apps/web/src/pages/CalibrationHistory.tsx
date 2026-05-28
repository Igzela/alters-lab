import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson, listActionAlignmentScores, listWeeklyReviews } from '../api'
import type { ActionAlignmentScore, VerdictLabel, WeeklyReviewSession } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

function getVerdictDescriptions(t: (key: string) => string): Record<VerdictLabel, string> {
  return {
    aligned_progress: t('history.verdictAligned'),
    noisy_progress: t('history.verdictNoisy'),
    avoidance_disguised_as_work: t('history.verdictAvoidance'),
    recovery_week: t('history.verdictRecovery'),
    unstable_but_useful: t('history.verdictUnstable'),
    blocked_by_environment: t('history.verdictBlocked'),
  }
}

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

  const { t } = useTranslation()

  if (error && !data) return <ErrorDisplay message={error} onRetry={() => { setError(''); window.location.reload() }} />
  if (!data) return <LoadingSpinner label={t('history.loading')} />

  const records = (data.records as Record<string, unknown>[]) || []
  const drift = (data.drift_evidence as Record<string, unknown>[]) || []
  const sortedScores = [...actionScores].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  const trend = getTrend(actionScores)
  const verdictDescriptions = getVerdictDescriptions(t)

  const trendArrowText = (tr: typeof trend) => {
    if (tr === 'up') return `↑ ${t('history.improving')}`
    if (tr === 'down') return `↓ ${t('history.declining')}`
    if (tr === 'stable') return `→ ${t('history.stable')}`
    return t('history.firstScore')
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{t('history.title')}</h2>

      <div className="p-3 mb-4 bg-blue-950/30 rounded-lg border border-blue-800/30">
        <h4 className="text-sm font-medium mb-1">{t('history.whatShows')}</h4>
        <p className="text-sm text-gray-300">{t('history.scoreExplanation')}</p>
        <p className="text-xs text-gray-400 mt-1">
          <strong>{t('history.weeklyReviews')}</strong> are sessions where you reflect on your week.
          <strong> {t('history.actionAlignment')}</strong> measure how well your actions matched your intentions.
          <strong> Calibration records</strong> are the raw score data.
        </p>
      </div>

      <h3 className="text-base font-medium">{t('history.weeklyReviews')} ({weeklyReviews.length})</h3>
      {weeklyReviews.length === 0 && <p className="text-gray-400 text-sm">{t('history.noReviews')}</p>}
      {weeklyReviews.map(session => (
        <div key={session.session_id} className="p-2 bg-gray-800/50 rounded text-sm">
          <strong>{session.session_id}</strong> — {session.status}<br />
          {t('history.note')} {session.weekly_note_record_id}<br />
          {session.created_at && <span className="text-xs text-gray-500">{t('history.created')} {session.created_at}</span>}<br />
          Next correction: {session.next_week_primary_correction || t('history.pending')}
        </div>
      ))}

      <h3 className="text-base font-medium">{t('history.actionAlignment')} ({actionScores.length}) {trendArrowText(trend)}</h3>
      {actionScores.length === 0 && <p className="text-gray-400 text-sm">{t('history.noScores')}</p>}
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
          {t('history.verdict')} {score.verdict_label.replace(/_/g, ' ')}<br />
          {score.created_at && <span className="text-xs text-gray-500">{score.created_at}</span>}

          {selectedScore?.score_id === score.score_id && (
            <div className="mt-2 p-3 bg-gray-800 rounded border border-gray-700">
              <h4 className="text-sm font-medium mb-2">{t('history.scoreDetail')}</h4>
              <p className="text-sm"><strong>{t('history.score')}</strong> {formatScore(score.action_alignment_score)} (0.0 = no alignment, 1.0 = full alignment)</p>
              <p className="text-sm"><strong>{t('history.verdict')}</strong> {verdictDescriptions[score.verdict_label] || score.verdict_label}</p>
              <p className="text-sm"><strong>{t('history.yourWords')}</strong> {score.verdict_sentence || t('history.none')}</p>
              <p className="text-sm mt-1"><strong>{t('history.dimensions')}</strong></p>
              <ul className="list-disc list-inside text-sm text-gray-300 ml-2">
                <li>{t('history.directionAlignment')} {formatScore(score.scores.direction_alignment)}</li>
                <li>{t('history.executionConsistency')} {formatScore(score.scores.execution_consistency)}</li>
                <li>{t('history.avoidanceLevel')} {formatScore(score.scores.avoidance_level)}</li>
              </ul>
              <p className="text-sm mt-1"><strong>{t('history.evidence')}</strong></p>
              <ul className="list-disc list-inside text-sm text-gray-300 ml-2">
                <li>{t('history.action')} {score.evidence.one_action_evidence || t('history.none')}</li>
                <li>{t('history.avoidance')} {score.evidence.one_avoidance_or_friction_evidence || t('history.none')}</li>
                <li>{t('history.nextCorrection')} {score.evidence.one_next_correction || t('history.none')}</li>
              </ul>
              <p className="text-xs text-gray-500 mt-2">{t('history.session')} {score.session_id}</p>
            </div>
          )}
        </div>
      ))}

      <h3 className="text-base font-medium">{t('history.scores')} ({String(data.count)})</h3>
      {records.length === 0 && <p className="text-gray-400 text-sm">{t('history.noRecords')}</p>}
      {records.map(r => (
        <div key={String(r.id)} className="p-2 bg-gray-800/30 rounded text-sm">
          <strong>{String(r.id)}</strong> — {String(r.alter_id)}<br />
          Actual: {JSON.stringify(r.actual_scores)}
        </div>
      ))}
      {drift.length > 0 && (
        <>
          <h3 className="text-base font-medium">{t('history.driftEvidence')}</h3>
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
