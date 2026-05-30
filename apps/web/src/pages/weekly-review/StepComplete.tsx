import { useTranslation } from 'react-i18next'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Badge } from '../../components/Badge'
import type { ActionAlignmentScore, WeeklyNoteRecord, WeeklyReviewSession } from '../../types'

type Props = {
  noteRecord: WeeklyNoteRecord
  session: WeeklyReviewSession
  score: ActionAlignmentScore
  onReset: () => void
}

export default function StepComplete({ noteRecord, session, score, onReset }: Props) {
  const { t } = useTranslation()
  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step6Title')}</h3>
      <div className="text-sm space-y-1" style={{ color: 'var(--color-text-secondary)' }}>
        <p>{t('weeklyReview.noteRecordId')} <Badge variant="info">{noteRecord.record_id}</Badge></p>
        <p>{t('weeklyReview.reviewSessionId')} <Badge variant="amber">{session.session_id}</Badge></p>
        <p>{t('weeklyReview.scoreRecordId')} <Badge variant="warning">{score.score_id}</Badge></p>
        <p>{t('weeklyReview.alignmentScore')} <strong className="font-mono">{score.action_alignment_score}</strong></p>
      </div>
      <p className="text-xs mt-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.weekEvidenceNote')}</p>
      <Button variant="secondary" className="mt-3" onClick={onReset}>{t('weeklyReview.resetFlow')}</Button>
    </Card>
  )
}
