import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useSubmitRealityScore, useActionAlignmentScores } from '../hooks/useApi'
import { Button } from '../components/Button'
import { TextArea } from '../components/Input'
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
  const mutation = useSubmitRealityScore()
  const recentScoresQuery = useActionAlignmentScores()

  const recentScores = recentScoresQuery.data
    ? [...(recentScoresQuery.data.scores || [])].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()).slice(0, 5)
    : []

  const submit = () => {
    setStatus('')
    mutation.mutate(
      {
        score_id: `score_manual_${Date.now()}`,
        branch_id: ALTERS[pair].branch,
        alter_id: ALTERS[pair].alter,
        actual_scores: scores,
        user_notes: notes,
        submitted_by_user: true,
        source: 'explicit_user_submission',
        caller: 'api',
      },
      {
        onSuccess: (res) => {
          const record = (res as Record<string, unknown>).record as Record<string, unknown> | undefined
          setStatus(`${t('realityScore.scoreRecorded')} ${record?.id || ''}`)
        },
      }
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('realityScore.title')}</h2>
      <p className="text-sm" style={{ color: '#78716c' }}>{t('realityScore.description')}</p>

      <Banner variant="warning">{t('realityScore.manualNote')}</Banner>

      <div className="flex gap-2">
        {onNavigate && (
          <Button variant="secondary" onClick={() => onNavigate('weekly')}>
            {t('realityScore.goToWeeklyReview')}
          </Button>
        )}
        {onNavigate && (
          <Button variant="ghost" onClick={() => onNavigate('history')}>
            {t('realityScore.viewHistory')}
          </Button>
        )}
      </div>

      {recentScores.length > 0 && (
        <Card accent="amber">
          <h4 className="text-sm font-medium mb-2">{t('realityScore.recentScores')}</h4>
          <p className="text-xs mb-2" style={{ color: '#a8a29e' }}>
            {t('realityScore.recentScoresDesc')}
          </p>
          {recentScores.map(s => (
            <div key={s.score_id} className="py-1 text-sm">
              <strong>{s.action_alignment_score.toFixed(2)}</strong> — {s.verdict_label.replace(/_/g, ' ')}
              {s.created_at && <span className="text-xs ml-2" style={{ color: '#a8a29e' }}>{s.created_at}</span>}
            </div>
          ))}
        </Card>
      )}

      <Select value={pair} onChange={e => setPair(Number(e.target.value))} className="mb-3">
        {ALTERS.map((a, i) => <option key={a.alter} value={i}>{a.alter} / {a.branch}</option>)}
      </Select>
      {DIMS.map(d => (
        <div key={d} className="flex items-center gap-3 text-sm">
          <label className="w-40" style={{ color: '#78716c' }}>{d}</label>
          <input type="range" min={1} max={5} value={scores[d]}
            onChange={e => setScores({ ...scores, [d]: Number(e.target.value) })} className="flex-1" />
          <span className="w-6 text-center font-mono" style={{ color: '#1c1917' }}>{scores[d]}</span>
        </div>
      ))}
      <TextArea
        value={notes}
        onChange={e => setNotes(e.target.value)}
        placeholder={t('realityScore.notesPlaceholder')}
        rows={3}
      />
      <Button variant="primary" onClick={submit} disabled={mutation.isPending}>
        {mutation.isPending ? t('realityScore.submitting') : t('realityScore.submitScore')}
      </Button>
      {status && <Banner variant="success">{status}</Banner>}
      {mutation.error && <ErrorDisplay message={(mutation.error as Error).message} />}
    </div>
  )
}
