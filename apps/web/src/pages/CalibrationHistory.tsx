import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson, listActionAlignmentScores, listWeeklyReviews } from '../api'
import { staggerFadeIn } from '../animations'
import { formatDate } from '../dateFormat'
import type { ActionAlignmentScore, VerdictLabel, WeeklyReviewSession } from '../types'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Skeleton } from '../components/Skeleton'
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
  const [retryCount, setRetryCount] = useState(0)
  const [selectedScore, setSelectedScore] = useState<ActionAlignmentScore | null>(null)
  const cardsRef = useRef<HTMLDivElement>(null)

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
  }, [retryCount])

  useEffect(() => {
    if (data && cardsRef.current) {
      const cards = cardsRef.current.querySelectorAll('[data-stagger]')
      staggerFadeIn(Array.from(cards) as HTMLElement[])
    }
  }, [data, weeklyReviews, actionScores])

  const { t } = useTranslation()

  if (error && !data) return <ErrorDisplay message={error} onRetry={() => { setError(''); setRetryCount(c => c + 1) }} />
  if (!data) return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('history.title')}</h2>
      <Skeleton lines={5} />
      <Skeleton lines={4} />
      <Skeleton lines={6} />
    </div>
  )

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

  const trendBadge: Record<typeof trend, 'success' | 'error' | 'info' | 'muted'> = {
    up: 'success',
    down: 'error',
    stable: 'info',
    first: 'muted',
  }

  return (
    <div ref={cardsRef} className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('history.title')}</h2>

      <Card accent="lilac">
        <h4 className="text-sm font-medium mb-1">{t('history.whatShows')}</h4>
        <p className="text-sm" style={{ color: '#c4c2b8' }}>{t('history.scoreExplanation')}</p>
        <p className="text-xs mt-1" style={{ color: '#7c7c6f' }}>
          <strong>{t('history.weeklyReviews')}</strong> are sessions where you reflect on your week.
          <strong> {t('history.actionAlignment')}</strong> measure how well your actions matched your intentions.
          <strong> Calibration records</strong> are the raw score data.
        </p>
      </Card>

      <h3 className="text-base font-medium">{t('history.weeklyReviews')} ({weeklyReviews.length})</h3>
      {weeklyReviews.length === 0 && <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('history.noReviews')}</p>}
      {weeklyReviews.map(session => (
        <Card key={session.session_id} data-stagger>
          <strong className="text-sm">{session.session_id}</strong> — <Badge variant="info">{session.status}</Badge><br />
          <span className="text-xs" style={{ color: '#7c7c6f' }}>
            {t('history.note')} {session.weekly_note_record_id}
          </span><br />
          {session.created_at && <span className="text-xs" style={{ color: '#7c7c6f' }}>{t('history.created')} {formatDate(session.created_at)}</span>}<br />
          <span className="text-xs" style={{ color: '#7c7c6f' }}>Next correction: {session.next_week_primary_correction || t('history.pending')}</span>
        </Card>
      ))}

      <h3 className="text-base font-medium">{t('history.actionAlignment')} ({actionScores.length}) <Badge variant={trendBadge[trend]}>{trendArrowText(trend)}</Badge></h3>
      {actionScores.length === 0 && <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('history.noScores')}</p>}
      {sortedScores.map(score => (
        <div
          key={score.score_id}
          data-stagger
          className="p-3 rounded-xl cursor-pointer transition-all duration-200 hover:bg-white/5"
          style={{
            backgroundColor: selectedScore?.score_id === score.score_id ? '#242624' : '#1a1c1a',
            border: selectedScore?.score_id === score.score_id ? '1px solid #9d95ff' : '1px solid #242624',
          }}
          onClick={() => setSelectedScore(selectedScore?.score_id === score.score_id ? null : score)}
        >
          <strong className="text-sm">{score.score_id}</strong> — {formatScore(score.action_alignment_score)}<br />
          <span className="text-xs" style={{ color: '#7c7c6f' }}>
            {t('history.verdict')} {score.verdict_label.replace(/_/g, ' ')}
          </span><br />
          {score.created_at && <span className="text-xs" style={{ color: '#7c7c6f' }}>{formatDate(score.created_at)}</span>}

          {selectedScore?.score_id === score.score_id && (
            <div className="mt-3 p-3 rounded-xl" style={{ backgroundColor: '#0e100f', border: '1px solid #242624' }}>
              <h4 className="text-sm font-medium mb-2">{t('history.scoreDetail')}</h4>
              <p className="text-sm"><strong>{t('history.score')}</strong> {formatScore(score.action_alignment_score)} (0.0 = no alignment, 1.0 = full alignment)</p>
              <p className="text-sm"><strong>{t('history.verdict')}</strong> {verdictDescriptions[score.verdict_label] || score.verdict_label}</p>
              <p className="text-sm"><strong>{t('history.yourWords')}</strong> {score.verdict_sentence || t('history.none')}</p>
              <p className="text-sm mt-1"><strong>{t('history.dimensions')}</strong></p>
              <ul className="list-disc list-inside text-sm ml-2" style={{ color: '#c4c2b8' }}>
                <li>{t('history.directionAlignment')} {formatScore(score.scores.direction_alignment)}</li>
                <li>{t('history.executionConsistency')} {formatScore(score.scores.execution_consistency)}</li>
                <li>{t('history.avoidanceLevel')} {formatScore(score.scores.avoidance_level)}</li>
              </ul>
              <p className="text-sm mt-1"><strong>{t('history.evidence')}</strong></p>
              <ul className="list-disc list-inside text-sm ml-2" style={{ color: '#c4c2b8' }}>
                <li>{t('history.action')} {score.evidence.one_action_evidence || t('history.none')}</li>
                <li>{t('history.avoidance')} {score.evidence.one_avoidance_or_friction_evidence || t('history.none')}</li>
                <li>{t('history.nextCorrection')} {score.evidence.one_next_correction || t('history.none')}</li>
              </ul>
              <p className="text-xs mt-2" style={{ color: '#7c7c6f' }}>{t('history.session')} {score.session_id}</p>
            </div>
          )}
        </div>
      ))}

      <h3 className="text-base font-medium">{t('history.scores')} ({String(data.count)})</h3>
      {records.length === 0 && <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('history.noRecords')}</p>}
      {records.map(r => (
        <Card key={String(r.id)}>
          <strong className="text-sm">{String(r.id)}</strong> — {String(r.alter_id)}<br />
          <span className="text-xs" style={{ color: '#c4c2b8' }}>Actual: {JSON.stringify(r.actual_scores)}</span>
        </Card>
      ))}
      {drift.length > 0 && (
        <>
          <h3 className="text-base font-medium">{t('history.driftEvidence')}</h3>
          {drift.map((d, i) => (
            <Card key={i} accent="orange">
              <span className="text-sm">
                Overall: {String(d.overall)} | Threshold exceeded: {String(d.threshold_exceeded)}
              </span>
            </Card>
          ))}
        </>
      )}
    </div>
  )
}
