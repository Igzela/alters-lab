import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { postJson, listActionAlignmentScores } from '../api'
import type { ActionAlignmentScore } from '../types'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Select } from '../components/Input'
import { Banner } from '../components/Banner'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

const ALTERS = [
  { alter: 'alter_A', branch: 'branch_A' },
  { alter: 'alter_B', branch: 'branch_B' },
  { alter: 'alter_C', branch: 'branch_C' },
  { alter: 'alter_D', branch: 'branch_D' },
]

const DIMS = ['execution_discipline', 'exploration_freedom', 'life_state_match', 'energy_level'] as const

export default function RealityScore({ onNavigate }: { onNavigate?: (page: string) => void }) {
  const { t } = useTranslation()
  const [pair, setPair] = useState(0)
  const [scores, setScores] = useState<Record<string, number>>({
    execution_discipline: 3,
    exploration_freedom: 3,
    life_state_match: 3,
    energy_level: 3,
  })
  const [notes, setNotes] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [recentScores, setRecentScores] = useState<ActionAlignmentScore[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [loadingScores, setLoadingScores] = useState(true)

  const loadScores = useCallback(() => {
    setLoadingScores(true)
    listActionAlignmentScores()
      .then(res => {
        const sorted = [...res.scores].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        setRecentScores(sorted.slice(0, 5))
      })
      .catch(() => {})
      .finally(() => setLoadingScores(false))
  }, [])

  useEffect(() => { loadScores() }, [loadScores])

  const submit = async () => {
    setError('')
    setStatus('')
    setSubmitting(true)
    try {
      const res = await postJson('/calibration-loop/reality-scores', {
        score_id: `score_manual_${Date.now()}`,
        branch_id: ALTERS[pair].branch,
        alter_id: ALTERS[pair].alter,
        actual_scores: scores,
        user_notes: notes,
        submitted_by_user: true,
        source: 'explicit_user_submission',
        caller: 'api',
      })
      setStatus(`${t('realityScore.scoreRecorded')} ${res.record.id}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('common.unknownError'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('realityScore.title')}</h2>
      <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('realityScore.description')}</p>

      <Banner variant="warning">{t('realityScore.manualNote')}</Banner>

      <div className="flex gap-2">
        {onNavigate && (
          <Button variant="secondary" accent="pink" onClick={() => onNavigate('weekly')}>
            {t('realityScore.goToWeeklyReview')}
          </Button>
        )}
        {onNavigate && (
          <Button variant="ghost" accent="pink" onClick={() => onNavigate('history')}>
            {t('realityScore.viewHistory')}
          </Button>
        )}
      </div>

      {recentScores.length > 0 && (
        <Card accent="pink">
          <h4 className="text-sm font-medium mb-2">{t('realityScore.recentScores')}</h4>
          <p className="text-xs mb-2" style={{ color: '#7c7c6f' }}>
            {t('realityScore.recentScoresDesc')}
          </p>
          {recentScores.map(s => (
            <div key={s.score_id} className="py-1 text-sm">
              <strong>{s.action_alignment_score.toFixed(2)}</strong> — {s.verdict_label.replace(/_/g, ' ')}
              {s.created_at && <span className="text-xs ml-2" style={{ color: '#7c7c6f' }}>{s.created_at}</span>}
            </div>
          ))}
        </Card>
      )}

      <Select value={pair} onChange={e => setPair(Number(e.target.value))} className="mb-3">
        {ALTERS.map((a, i) => <option key={a.alter} value={i}>{a.alter} / {a.branch}</option>)}
      </Select>
      {DIMS.map(d => (
        <div key={d} className="flex items-center gap-3 text-sm">
          <label className="w-40" style={{ color: '#c4c2b8' }}>{d}</label>
          <input type="range" min={1} max={5} value={scores[d]}
            onChange={e => setScores({ ...scores, [d]: Number(e.target.value) })} className="flex-1" />
          <span className="w-6 text-center" style={{ color: '#fffce1' }}>{scores[d]}</span>
        </div>
      ))}
      <textarea
        className="w-full px-3 py-2 text-sm rounded-lg border outline-none transition-colors min-h-[60px]"
        style={{ backgroundColor: '#1a1c1a', color: '#fffce1', borderColor: '#42433d' }}
        value={notes}
        onChange={e => setNotes(e.target.value)}
        placeholder={t('realityScore.notesPlaceholder')}
      />
      <Button variant="primary" accent="pink" onClick={submit} disabled={submitting}>
        {submitting ? t('realityScore.submitting') : t('realityScore.submitScore')}
      </Button>
      {status && <Banner variant="success">{status}</Banner>}
      {error && <ErrorDisplay message={error} />}
    </div>
  )
}
