import { useTranslation } from 'react-i18next'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Input, Field, Select, TextArea } from '../../components/Input'
import type { WeeklyNoteRecord } from '../../types'

type Props = {
  noteRecord: WeeklyNoteRecord
  editRecord: WeeklyNoteRecord
  setEditRecord: (r: WeeklyNoteRecord) => void
  editEnabled: boolean
  setEditEnabled: (v: boolean) => void
  correctionNote: string
  setCorrectionNote: (v: string) => void
  loading: string
  onSaveEdit: () => void
  onContinue: () => void
}

export default function StepNoteEdit({
  noteRecord, editRecord, setEditRecord, editEnabled, setEditEnabled,
  correctionNote, setCorrectionNote, loading, onSaveEdit, onContinue,
}: Props) {
  const { t } = useTranslation()
  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step2Title')}</h3>
      <p className="text-sm mb-2" style={{ color: 'var(--color-text-secondary)' }}>{t('weeklyReview.rawNotePreserved')} {noteRecord.raw_note_preserved ? t('common.yes') : t('common.no')}</p>
      <Field label="session_type">
        {editEnabled ? (
          <Select value={editRecord.session_type} onChange={e => setEditRecord({ ...editRecord, session_type: e.target.value as WeeklyNoteRecord['session_type'] })}>
            <option value="personal">{t('weeklyReview.typePersonal')}</option>
            <option value="project">{t('weeklyReview.typeProject')}</option>
            <option value="learning">{t('weeklyReview.typeLearning')}</option>
            <option value="relationship">{t('weeklyReview.typeRelationship')}</option>
          </Select>
        ) : (
          <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{noteRecord.session_type}</span>
        )}
      </Field>
      <Field label="observable_facts">
        {editEnabled ? (
          <TextArea
            value={editRecord.observable_facts.join('\n')}
            onChange={e => setEditRecord({ ...editRecord, observable_facts: e.target.value.split('\n').map(v => v.trim()).filter(Boolean) })}
            rows={4}
          />
        ) : (
          <ul className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{noteRecord.observable_facts.map((fact, i) => <li key={i}>{fact}</li>)}</ul>
        )}
      </Field>
      <Field label="subjective_state">
        {editEnabled ? <Input value={editRecord.subjective_state} onChange={e => setEditRecord({ ...editRecord, subjective_state: e.target.value })} /> : <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{noteRecord.subjective_state}</span>}
      </Field>
      <Field label="primary_problem">
        {editEnabled ? <Input value={editRecord.primary_problem} onChange={e => setEditRecord({ ...editRecord, primary_problem: e.target.value })} /> : <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{noteRecord.primary_problem}</span>}
      </Field>
      <Field label="friction_or_avoidance_point">
        {editEnabled ? <Input value={editRecord.friction_or_avoidance_point} onChange={e => setEditRecord({ ...editRecord, friction_or_avoidance_point: e.target.value })} /> : <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{noteRecord.friction_or_avoidance_point}</span>}
      </Field>
      <Field label="desired_correction / primary correction">
        {editEnabled ? <Input value={editRecord.desired_correction} onChange={e => setEditRecord({ ...editRecord, desired_correction: e.target.value })} /> : <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{noteRecord.desired_correction}</span>}
      </Field>
      {editEnabled && (
        <Field label="correction_note">
          <Input value={correctionNote} onChange={e => setCorrectionNote(e.target.value)} />
        </Field>
      )}
      <div className="flex gap-2 flex-wrap">
        <Button variant="secondary" onClick={() => setEditEnabled(!editEnabled)}>
          {editEnabled ? t('weeklyReview.cancelEdit') : t('weeklyReview.editFields')}
        </Button>
        {editEnabled && <Button variant="primary" onClick={onSaveEdit} disabled={!!loading || !correctionNote.trim()}>{t('weeklyReview.saveEdit')}</Button>}
        <Button variant="ghost" onClick={onContinue}>{t('weeklyReview.continue')}</Button>
      </div>
    </Card>
  )
}
