import { useTranslation } from 'react-i18next'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Input, Field, Select } from '../../components/Input'
import { Badge } from '../../components/Badge'
import type { ActionAlignmentScore, VerdictLabel } from '../../types'
import { VERDICTS, VERDICT_DESCRIPTIONS } from './types'

type Props = {
  directionAlignment: number
  setDirectionAlignment: (v: number) => void
  executionConsistency: number
  setExecutionConsistency: (v: number) => void
  avoidanceLevel: number
  setAvoidanceLevel: (v: number) => void
  oneActionEvidence: string
  setOneActionEvidence: (v: string) => void
  oneAvoidanceEvidence: string
  setOneAvoidanceEvidence: (v: string) => void
  oneNextCorrection: string
  setOneNextCorrection: (v: string) => void
  verdictLabel: VerdictLabel
  setVerdictLabel: (v: VerdictLabel) => void
  verdictSentence: string
  setVerdictSentence: (v: string) => void
  score: ActionAlignmentScore | null
  scorePath: string | null
  loading: string
  onSubmitScore: () => void
}

export default function StepScoring({
  directionAlignment, setDirectionAlignment, executionConsistency, setExecutionConsistency,
  avoidanceLevel, setAvoidanceLevel, oneActionEvidence, setOneActionEvidence,
  oneAvoidanceEvidence, setOneAvoidanceEvidence, oneNextCorrection, setOneNextCorrection,
  verdictLabel, setVerdictLabel, verdictSentence, setVerdictSentence,
  score, scorePath, loading, onSubmitScore,
}: Props) {
  const { t } = useTranslation()
  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step5Title')}</h3>
      <Slider label={t('weeklyReview.directionQuestion')} value={directionAlignment} onChange={setDirectionAlignment} />
      <Slider label={t('weeklyReview.consistencyQuestion')} value={executionConsistency} onChange={setExecutionConsistency} />
      <Slider label={t('weeklyReview.avoidanceQuestion')} value={avoidanceLevel} onChange={setAvoidanceLevel} />
      <Field label={t('weeklyReview.actionEvidence')}>
        <Input value={oneActionEvidence} onChange={e => setOneActionEvidence(e.target.value)} />
      </Field>
      <Field label={t('weeklyReview.avoidanceEvidence')}>
        <Input value={oneAvoidanceEvidence} onChange={e => setOneAvoidanceEvidence(e.target.value)} />
      </Field>
      <Field label={t('weeklyReview.nextCorrectionEvidence')}>
        <Input value={oneNextCorrection} onChange={e => setOneNextCorrection(e.target.value)} />
      </Field>
      <Field label={t('weeklyReview.verdictLabel')}>
        <Select value={verdictLabel} onChange={e => setVerdictLabel(e.target.value as VerdictLabel)}>
          {VERDICTS.map(v => <option key={v} value={v}>{v.replace(/_/g, ' ')}</option>)}
        </Select>
        <span className="text-sm mt-0.5" style={{ color: 'var(--color-text-muted)' }}>{VERDICT_DESCRIPTIONS[verdictLabel]}</span>
      </Field>
      <Field label={t('weeklyReview.verdictSentence')}>
        <Input value={verdictSentence} onChange={e => setVerdictSentence(e.target.value)} />
      </Field>
      <Button
        variant="primary"
        onClick={onSubmitScore}
        disabled={!!loading || !oneActionEvidence.trim() || !oneAvoidanceEvidence.trim() || !oneNextCorrection.trim() || !verdictSentence.trim()}
      >
        {loading === 'saving score' ? t('weeklyReview.saving') : t('weeklyReview.saveAlignment')}
      </Button>
      {score && (
        <div className="mt-2 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          <p>{t('weeklyReview.scoreId')} <Badge variant="info">{score.score_id}</Badge></p>
          <p>{t('weeklyReview.alignmentScore')} <strong className="font-mono">{score.action_alignment_score}</strong></p>
          {scorePath && <p>{t('weeklyReview.savedPath')} <span style={{ color: 'var(--color-text-muted)' }}>{scorePath}</span></p>}
        </div>
      )}
    </Card>
  )
}

function Slider({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <label className="grid gap-1.5 mb-3">
      <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{label}</span>
      <div className="flex items-center gap-2.5">
        <input className="flex-1" type="range" min={0} max={1} step={0.05} value={value} onChange={e => onChange(Number(e.target.value))} />
        <Input className="max-w-[120px] font-mono" type="number" min={0} max={1} step={0.05} value={value} onChange={e => onChange(Number(e.target.value))} />
      </div>
    </label>
  )
}
