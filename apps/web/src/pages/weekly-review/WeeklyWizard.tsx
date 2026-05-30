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
} from '../../api'
import type { ActionAlignmentScore, VerdictLabel, WeeklyNoteRecord, WeeklyReviewSession } from '../../types'
import { Banner } from '../../components/Banner'
import P6Progress from '../P6Progress'
import type { Step, AlterOption } from './types'
import StepNoteIngest from './StepNoteIngest'
import StepNoteEdit from './StepNoteEdit'
import StepReview from './StepReview'
import StepAssistant from './StepAssistant'
import StepScoring from './StepScoring'
import StepComplete from './StepComplete'

export default function WeeklyWizard() {
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

  const startReviewAction = () => run('starting review', async () => {
    if (!noteRecord) return
    const result = await startWeeklyReview(noteRecord.record_id, selectedAlter || null)
    setSession(result.session)
    setMessage(`${t('weeklyReview.reviewStarted')} ${result.session.session_id}`)
    setStep(4)
  })

  const completeReviewAction = () => run('completing review', async () => {
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
        <StepNoteIngest
          rawNote={rawNote}
          setRawNote={setRawNote}
          noteRecord={noteRecord}
          loading={loading}
          onIngest={ingest}
        />
      )}

      {step === 2 && noteRecord && editRecord && (
        <StepNoteEdit
          noteRecord={noteRecord}
          editRecord={editRecord}
          setEditRecord={setEditRecord}
          editEnabled={editEnabled}
          setEditEnabled={setEditEnabled}
          correctionNote={correctionNote}
          setCorrectionNote={setCorrectionNote}
          loading={loading}
          onSaveEdit={saveEdit}
          onContinue={() => setStep(3)}
        />
      )}

      {step === 3 && noteRecord && (
        <StepReview
          selectedAlter={selectedAlter}
          setSelectedAlter={setSelectedAlter}
          alterOptions={alterOptions}
          session={session}
          loading={loading}
          onStartReview={startReviewAction}
        />
      )}

      {step === 4 && session && (
        <StepAssistant
          session={session}
          reviewNote={reviewNote}
          setReviewNote={setReviewNote}
          dialogueSummary={dialogueSummary}
          setDialogueSummary={setDialogueSummary}
          primaryNextCorrection={primaryNextCorrection}
          setPrimaryNextCorrection={setPrimaryNextCorrection}
          supportingAction1={supportingAction1}
          setSupportingAction1={setSupportingAction1}
          supportingAction2={supportingAction2}
          setSupportingAction2={setSupportingAction2}
          assistantHelp={assistantHelp}
          setAssistantHelp={setAssistantHelp}
          assistantSuggestion={assistantSuggestion}
          assistantStatus={assistantStatus}
          assistantLiveConfirmation={assistantLiveConfirmation}
          setAssistantLiveConfirmation={setAssistantLiveConfirmation}
          assistantLoading={assistantLoading}
          assistantError={assistantError}
          loading={loading}
          onCheckProvider={loadAssistantStatus}
          onGenerateSuggestion={generateSuggestion}
          onCompleteReview={completeReviewAction}
        />
      )}

      {step === 5 && session && (
        <StepScoring
          directionAlignment={directionAlignment}
          setDirectionAlignment={setDirectionAlignment}
          executionConsistency={executionConsistency}
          setExecutionConsistency={setExecutionConsistency}
          avoidanceLevel={avoidanceLevel}
          setAvoidanceLevel={setAvoidanceLevel}
          oneActionEvidence={oneActionEvidence}
          setOneActionEvidence={setOneActionEvidence}
          oneAvoidanceEvidence={oneAvoidanceEvidence}
          setOneAvoidanceEvidence={setOneAvoidanceEvidence}
          oneNextCorrection={oneNextCorrection}
          setOneNextCorrection={setOneNextCorrection}
          verdictLabel={verdictLabel}
          setVerdictLabel={setVerdictLabel}
          verdictSentence={verdictSentence}
          setVerdictSentence={setVerdictSentence}
          score={score}
          scorePath={scorePath}
          loading={loading}
          onSubmitScore={submitScore}
        />
      )}

      {step === 6 && noteRecord && session && score && (
        <StepComplete
          noteRecord={noteRecord}
          session={session}
          score={score}
          onReset={reset}
        />
      )}
    </div>
  )
}
