import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  completeWeeklyReview,
  editWeeklyNote,
  fetchJson,
  fetchWeeklyReviewAssistantStatus,
  ingestWeeklyNote,
  scoreActionAlignment,
  startWeeklyReview,
  suggestWeeklyReviewAssistant,
} from '../api'
import type { ActionAlignmentScore, VerdictLabel, WeeklyNoteRecord, WeeklyReviewSession } from '../types'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input, Field, Select, TextArea } from '../components/Input'
import { Badge } from '../components/Badge'
import { Banner } from '../components/Banner'
import P6Progress from './P6Progress'

const today = new Date().toISOString().slice(0, 10)

const NOTE_TEMPLATE = `# Weekly Review - ${today}

## Session Type
personal / project / learning / relationship

## Observable Facts
-
-
-
-
-

## Subjective State
1-3 sentences.

## Primary Problem
One sentence.

## Friction / Avoidance
One concrete friction or avoidance point.

## Desired Correction
One primary correction for next week.
`

const verdicts: VerdictLabel[] = [
  'aligned_progress',
  'noisy_progress',
  'avoidance_disguised_as_work',
  'recovery_week',
  'unstable_but_useful',
  'blocked_by_environment',
]

const VERDICT_DESCRIPTIONS: Record<VerdictLabel, string> = {
  aligned_progress: 'Actions matched your stated direction. You did what you intended.',
  noisy_progress: 'You made progress, but not in your intended direction. Some drift.',
  avoidance_disguised_as_work: 'Activity looked productive but avoided the real problem.',
  recovery_week: 'You bounced back from a stall or setback. Restorative week.',
  unstable_but_useful: 'Inconsistent, but some meaningful progress happened.',
  blocked_by_environment: 'External factors prevented progress despite intention.',
}

type AlterOption = { id: string; name: string }

type Step = 1 | 2 | 3 | 4 | 5 | 6

export default function WeeklyReview() {
  const { t } = useTranslation()
  const [step, setStep] = useState<Step>(1)
  const [rawNote, setRawNote] = useState('')
  const [noteRecord, setNoteRecord] = useState<WeeklyNoteRecord | null>(null)
  const [selectedAlter, setSelectedAlter] = useState('')
  const [session, setSession] = useState<WeeklyReviewSession | null>(null)
  const [score, setScore] = useState<ActionAlignmentScore | null>(null)
  const [scorePath, setScorePath] = useState<string | null>(null)
  const [loading, setLoading] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const [editEnabled, setEditEnabled] = useState(false)
  const [editRecord, setEditRecord] = useState<WeeklyNoteRecord | null>(null)
  const [correctionNote, setCorrectionNote] = useState('')

  const [reviewNote, setReviewNote] = useState('')
  const [dialogueSummary, setDialogueSummary] = useState('')
  const [primaryNextCorrection, setPrimaryNextCorrection] = useState('')
  const [supportingAction1, setSupportingAction1] = useState('')
  const [supportingAction2, setSupportingAction2] = useState('')

  const [directionAlignment, setDirectionAlignment] = useState(0.5)
  const [executionConsistency, setExecutionConsistency] = useState(0.5)
  const [avoidanceLevel, setAvoidanceLevel] = useState(0.5)
  const [oneActionEvidence, setOneActionEvidence] = useState('')
  const [oneAvoidanceEvidence, setOneAvoidanceEvidence] = useState('')
  const [oneNextCorrection, setOneNextCorrection] = useState('')
  const [verdictLabel, setVerdictLabel] = useState<VerdictLabel>('unstable_but_useful')
  const [verdictSentence, setVerdictSentence] = useState('')

  const [assistantHelp, setAssistantHelp] = useState('general_review_suggestion')
  const [assistantSuggestion, setAssistantSuggestion] = useState('')
  const [assistantStatus, setAssistantStatus] = useState<{ provider_mode: string; configured: boolean } | null>(null)
  const [assistantLiveConfirmation, setAssistantLiveConfirmation] = useState('')
  const [assistantLoading, setAssistantLoading] = useState(false)
  const [assistantError, setAssistantError] = useState('')

  const [alterOptions, setAlterOptions] = useState<AlterOption[]>([
    { id: 'alter_A', name: 'alter_A' },
    { id: 'alter_B', name: 'alter_B' },
    { id: 'alter_C', name: 'alter_C' },
    { id: 'alter_D', name: 'alter_D' },
  ])

  useEffect(() => {
    fetchJson('/alter-dialogue/alters')
      .then((res: unknown) => {
        const data = res as { alters?: { alter_id: string }[] }
        if (data.alters && data.alters.length > 0) {
          setAlterOptions(data.alters.map(a => ({ id: a.alter_id, name: a.alter_id })))
        }
      })
      .catch(() => {})
  }, [])

  const run = async (label: string, task: () => Promise<void>) => {
    setLoading(label)
    setError('')
    setMessage('')
    try {
      await task()
    } catch (e) {
      setError(e instanceof Error ? e.message : t('weeklyReview.unknownError'))
    } finally {
      setLoading('')
    }
  }

  const ingest = () => run('ingesting', async () => {
    const result = await ingestWeeklyNote(rawNote)
    setNoteRecord(result.record)
    setEditRecord(result.record)
    setPrimaryNextCorrection(result.record.desired_correction)
    setOneNextCorrection(result.record.desired_correction)
    setMessage(`${t('weeklyReview.savedNote')} ${result.record.record_id}`)
    setStep(2)
  })

  const saveEdit = () => run('saving edit', async () => {
    if (!noteRecord || !editRecord) return
    const result = await editWeeklyNote(noteRecord.record_id, {
      session_type: editRecord.session_type,
      observable_facts: editRecord.observable_facts,
      subjective_state: editRecord.subjective_state,
      primary_problem: editRecord.primary_problem,
      friction_or_avoidance_point: editRecord.friction_or_avoidance_point,
      desired_correction: editRecord.desired_correction,
      correction_note: correctionNote,
    })
    setNoteRecord(result.record)
    setEditRecord(result.record)
    setEditEnabled(false)
    setCorrectionNote('')
    setMessage(t('weeklyReview.fieldsUpdated'))
  })

  const startReview = () => run('starting review', async () => {
    if (!noteRecord) return
    const result = await startWeeklyReview(noteRecord.record_id, selectedAlter || null)
    setSession(result.session)
    setMessage(`${t('weeklyReview.reviewStarted')} ${result.session.session_id}`)
    setStep(4)
  })

  const completeReview = () => run('completing review', async () => {
    if (!session) return
    const actions = [supportingAction1, supportingAction2].map(a => a.trim()).filter(Boolean)
    const result = await completeWeeklyReview(session.session_id, {
      review_note: reviewNote,
      dialogue_summary: dialogueSummary,
      primary_next_correction: primaryNextCorrection,
      supporting_actions: actions,
    })
    setSession(result.session)
    setOneNextCorrection(result.session.next_week_primary_correction || primaryNextCorrection)
    setMessage(t('weeklyReview.reviewCompleted'))
    setStep(5)
  })

  const submitScore = () => run('saving score', async () => {
    if (!session) return
    const result = await scoreActionAlignment({
      session_id: session.session_id,
      scores: {
        direction_alignment: directionAlignment,
        execution_consistency: executionConsistency,
        avoidance_level: avoidanceLevel,
      },
      evidence: {
        one_action_evidence: oneActionEvidence,
        one_avoidance_or_friction_evidence: oneAvoidanceEvidence,
        one_next_correction: oneNextCorrection,
      },
      verdict_label: verdictLabel,
      verdict_sentence: verdictSentence,
      save: true,
    })
    setScore(result.score)
    setScorePath(result.score_path)
    setMessage(`${t('weeklyReview.alignmentSaved')} ${result.score.score_id}`)
    setStep(6)
  })

  const reset = () => {
    setStep(1)
    setRawNote('')
    setNoteRecord(null)
    setEditRecord(null)
    setSelectedAlter('')
    setSession(null)
    setScore(null)
    setScorePath(null)
    setError('')
    setMessage('')
    setAssistantSuggestion('')
    setAssistantLiveConfirmation('')
    setAssistantError('')
  }

  const loadAssistantStatus = async () => {
    try {
      const s = await fetchWeeklyReviewAssistantStatus()
      setAssistantStatus(s)
    } catch {
      setAssistantStatus({ provider_mode: 'disabled', configured: false })
    }
  }

  const generateSuggestion = (live: boolean) => run('generating suggestion', async () => {
    setAssistantError('')
    setAssistantSuggestion('')
    const body: Parameters<typeof suggestWeeklyReviewAssistant>[0] = {
      requested_help: assistantHelp,
      dry_run: !live,
      live_generation: live,
    }
    if (live) body.confirmation = assistantLiveConfirmation || null
    if (noteRecord) body.weekly_note_record_id = noteRecord.record_id
    if (session) body.weekly_review_session_id = session.session_id
    if (reviewNote) body.review_context = `Current review note: ${reviewNote}`
    const result = await suggestWeeklyReviewAssistant(body)
    if (result.suggestion) {
      setAssistantSuggestion(result.suggestion)
    } else {
      setAssistantError(result.message)
    }
  })

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('weeklyReview.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('weeklyReview.description')}</p>
      <P6Progress />

      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{step}/6</span>
          <div className="flex-1 h-1 rounded-full" style={{ backgroundColor: 'var(--color-border)' }}>
            <div className="h-1 rounded-full transition-all duration-300" style={{ backgroundColor: 'var(--color-accent)', width: `${(step / 6) * 100}%` }} />
          </div>
        </div>
        <div className="flex gap-2 flex-wrap">
        {[1, 2, 3, 4, 5, 6].map(n => (
          <button
            key={n}
            className="px-3 py-1.5 text-sm rounded-lg transition-all duration-200 border-none cursor-pointer"
            style={{
              backgroundColor: step === n ? 'var(--color-text)' : 'transparent',
              color: step === n ? 'var(--color-bg)' : 'var(--color-text-muted)',
            }}
            type="button"
            onClick={() => setStep(n as Step)}
            disabled={n > 1 && !noteRecord}
          >
            {t(`weeklyReview.step${n}`)}
          </button>
        ))}
        </div>
      </div>

      {error && <Banner variant="error">{t('weeklyReview.error')} {error}</Banner>}
      {message && <Banner variant="success">{message}</Banner>}

      {step === 1 && (
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
            <Button variant="primary" onClick={ingest} disabled={!!loading || !rawNote.trim()}>
              {loading === 'ingesting' ? t('weeklyReview.ingesting') : t('weeklyReview.ingestNote')}
            </Button>
          </div>
          {noteRecord && <p className="text-sm mt-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.savedRecordId')} {noteRecord.record_id}</p>}
        </Card>
      )}

      {step === 2 && noteRecord && editRecord && (
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
            {editEnabled && <Button variant="primary" onClick={saveEdit} disabled={!!loading || !correctionNote.trim()}>{t('weeklyReview.saveEdit')}</Button>}
            <Button variant="ghost" onClick={() => setStep(3)}>{t('weeklyReview.continue')}</Button>
          </div>
        </Card>
      )}

      {step === 3 && noteRecord && (
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
          <Button variant="primary" onClick={startReview} disabled={!!loading}>
            {loading === 'starting review' ? t('weeklyReview.starting') : t('weeklyReview.startReview')}
          </Button>
          {session && <p className="text-sm mt-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.sessionId')} {session.session_id}</p>}
        </Card>
      )}

      {step === 4 && session && (
        <Card>
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step4Title')}</h3>
          <Field label={t('weeklyReview.reviewNote')}>
            <TextArea value={reviewNote} onChange={e => setReviewNote(e.target.value)} rows={4} />
          </Field>
          <Field label={t('weeklyReview.dialogueSummary')}>
            <TextArea value={dialogueSummary} onChange={e => setDialogueSummary(e.target.value)} rows={4} />
          </Field>
          <Field label={t('weeklyReview.primaryNextCorrection')}>
            <Input value={primaryNextCorrection} onChange={e => setPrimaryNextCorrection(e.target.value)} />
          </Field>
          <Field label={t('weeklyReview.supportingAction1')}>
            <Input value={supportingAction1} onChange={e => setSupportingAction1(e.target.value)} />
          </Field>
          <Field label={t('weeklyReview.supportingAction2')}>
            <Input value={supportingAction2} onChange={e => setSupportingAction2(e.target.value)} />
          </Field>

          <Card variant="raised">
            <h4 className="text-sm font-medium mb-1.5">{t('weeklyReview.assistantSuggestion')}</h4>
            <p className="text-xs mb-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.providerAdvisory')}</p>
            <Field label={t('weeklyReview.requestedHelp')}>
              <Select value={assistantHelp} onChange={e => setAssistantHelp(e.target.value)}>
                <option value="general_review_suggestion">{t('weeklyReview.generalSuggestion')}</option>
                <option value="summarize_facts">{t('weeklyReview.summarizeFacts')}</option>
                <option value="identify_friction">{t('weeklyReview.identifyFriction')}</option>
                <option value="draft_primary_correction">{t('weeklyReview.draftCorrection')}</option>
                <option value="suggest_supporting_actions">{t('weeklyReview.suggestActions')}</option>
                <option value="challenge_avoidance">{t('weeklyReview.challengeAvoidance')}</option>
              </Select>
            </Field>
            <div className="flex gap-2 flex-wrap mb-2.5">
              <Button variant="secondary" onClick={() => loadAssistantStatus()} disabled={assistantLoading}>
                {t('weeklyReview.checkProvider')}
              </Button>
              <Button variant="secondary" onClick={() => generateSuggestion(false)} disabled={!!loading || assistantLoading}>
                {loading === 'generating suggestion' ? t('weeklyReview.generating') : t('weeklyReview.generateDryRun')}
              </Button>
            </div>
            {assistantStatus && (
              <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.providerMode')} {assistantStatus.provider_mode} | {t('provider.configured')} <Badge variant={assistantStatus.configured ? 'success' : 'muted'}>{assistantStatus.configured ? 'yes' : 'no'}</Badge></p>
            )}
            {assistantStatus?.configured && assistantStatus.provider_mode === 'openai-compatible-http' && (
              <div className="mt-2">
                <Field label={t('weeklyReview.liveConfirmation')}>
                  <Input value={assistantLiveConfirmation} onChange={e => setAssistantLiveConfirmation(e.target.value)} placeholder="run-live-weekly-review-assistant" />
                </Field>
                <Button variant="primary" onClick={() => generateSuggestion(true)} disabled={!!loading || assistantLoading || assistantLiveConfirmation !== 'run-live-weekly-review-assistant'}>
                  {t('weeklyReview.generateLive')}
                </Button>
              </div>
            )}
            {assistantError && <Banner variant="error" className="mt-2">{assistantError}</Banner>}
            {assistantSuggestion && (
              <div className="mt-3 p-3 rounded-xl" style={{ backgroundColor: 'var(--color-accent-light)', color: 'var(--color-text)' }}>
                <p className="text-xs font-semibold mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>{t('weeklyReview.unverifiedSuggestion')}</p>
                <pre className="whitespace-pre-wrap text-sm m-0" style={{ color: 'var(--color-text)' }}>{assistantSuggestion}</pre>
                <div className="flex gap-2 mt-2 flex-wrap">
                  <Button variant="secondary" onClick={() => setReviewNote(assistantSuggestion)}>
                    {t('weeklyReview.copyToReviewNote')}
                  </Button>
                  <Button variant="secondary" onClick={() => setDialogueSummary(assistantSuggestion)}>
                    {t('weeklyReview.copyToDialogue')}
                  </Button>
                  <Button variant="secondary" onClick={() => setPrimaryNextCorrection(assistantSuggestion)}>
                    {t('weeklyReview.copyToCorrection')}
                  </Button>
                </div>
              </div>
            )}
          </Card>

          <div className="mt-3">
            <Button variant="primary" onClick={completeReview} disabled={!!loading || !reviewNote.trim() || !primaryNextCorrection.trim()}>
              {loading === 'completing review' ? t('weeklyReview.completing') : t('weeklyReview.completeReview')}
            </Button>
          </div>
          {session.status === 'completed' && (
            <div className="mt-2 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              <p>{t('weeklyReview.statusCompleted')}</p>
              <p>{t('weeklyReview.nextCorrection')} {session.next_week_primary_correction}</p>
              <p>{t('weeklyReview.supportingActions')} {session.supporting_actions.join(', ') || t('weeklyReview.none')}</p>
            </div>
          )}
        </Card>
      )}

      {step === 5 && session && (
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
              {verdicts.map(v => <option key={v} value={v}>{v.replace(/_/g, ' ')}</option>)}
            </Select>
            <span className="text-sm mt-0.5" style={{ color: 'var(--color-text-muted)' }}>{VERDICT_DESCRIPTIONS[verdictLabel]}</span>
          </Field>
          <Field label={t('weeklyReview.verdictSentence')}>
            <Input value={verdictSentence} onChange={e => setVerdictSentence(e.target.value)} />
          </Field>
          <Button
            variant="primary"
            onClick={submitScore}
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
      )}

      {step === 6 && noteRecord && session && score && (
        <Card>
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step6Title')}</h3>
          <div className="text-sm space-y-1" style={{ color: 'var(--color-text-secondary)' }}>
            <p>{t('weeklyReview.noteRecordId')} <Badge variant="info">{noteRecord.record_id}</Badge></p>
            <p>{t('weeklyReview.reviewSessionId')} <Badge variant="amber">{session.session_id}</Badge></p>
            <p>{t('weeklyReview.scoreRecordId')} <Badge variant="warning">{score.score_id}</Badge></p>
            <p>{t('weeklyReview.alignmentScore')} <strong className="font-mono">{score.action_alignment_score}</strong></p>
          </div>
          <p className="text-xs mt-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.weekEvidenceNote')}</p>
          <Button variant="secondary" className="mt-3" onClick={reset}>{t('weeklyReview.resetFlow')}</Button>
        </Card>
      )}
    </div>
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
