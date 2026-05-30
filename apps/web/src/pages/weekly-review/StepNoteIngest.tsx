import { useTranslation } from 'react-i18next'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { TextArea } from '../../components/Input'
import type { WeeklyNoteRecord } from '../../types'
import { NOTE_TEMPLATE } from './types'

type Props = {
  rawNote: string
  setRawNote: (v: string) => void
  noteRecord: WeeklyNoteRecord | null
  loading: string
  onIngest: () => void
}

export default function StepNoteIngest({ rawNote, setRawNote, noteRecord, loading, onIngest }: Props) {
  const { t } = useTranslation()
  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step1Title')}</h3>
      <Button variant="secondary" className="mb-3" onClick={() => setRawNote(NOTE_TEMPLATE)}>
        {t('weeklyReview.useTemplate')}
      </Button>
      <TextArea
        value={rawNote}
        onChange={e => setRawNote(e.target.value)}
        placeholder={NOTE_TEMPLATE}
        rows={12}
      />
      <div className="mt-3">
        <Button variant="primary" onClick={onIngest} disabled={!!loading || !rawNote.trim()}>
          {loading === 'ingesting' ? t('weeklyReview.ingesting') : t('weeklyReview.ingestNote')}
        </Button>
      </div>
      {noteRecord && <p className="text-sm mt-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.savedRecordId')} {noteRecord.record_id}</p>}
    </Card>
  )
}
