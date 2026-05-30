import { useTranslation } from 'react-i18next'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Field, Select } from '../../components/Input'
import type { WeeklyReviewSession } from '../../types'
import type { AlterOption } from './types'

type Props = {
  selectedAlter: string
  setSelectedAlter: (v: string) => void
  alterOptions: AlterOption[]
  session: WeeklyReviewSession | null
  loading: string
  onStartReview: () => void
}

export default function StepReview({ selectedAlter, setSelectedAlter, alterOptions, session, loading, onStartReview }: Props) {
  const { t } = useTranslation()
  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step3Title')}</h3>
      <Field label={t('weeklyReview.selectAlter')}>
        <Select value={selectedAlter} onChange={e => setSelectedAlter(e.target.value)}>
          <option value="">{t('weeklyReview.systemRecommended')}</option>
          {alterOptions.map(a => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </Select>
      </Field>
      <Button variant="primary" onClick={onStartReview} disabled={!!loading}>
        {loading === 'starting review' ? t('weeklyReview.starting') : t('weeklyReview.startReview')}
      </Button>
      {session && <p className="text-sm mt-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.sessionId')} {session.session_id}</p>}
    </Card>
  )
}
