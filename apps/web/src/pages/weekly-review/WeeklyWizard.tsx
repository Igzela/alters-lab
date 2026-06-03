import { useReducer, useEffect } from 'react'
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
import { Banner } from '../../components/Banner'
import P6Progress from '../P6Progress'
import StepNoteIngest from './StepNoteIngest'
import StepNoteEdit from './StepNoteEdit'
import StepReview from './StepReview'
import StepAssistant from './StepAssistant'
import StepScoring from './StepScoring'
import StepComplete from './StepComplete'
import { wizardReducer, INITIAL_WIZARD_STATE } from './wizardReducer'
import type { WizardAction } from './wizardReducer'

export default function WeeklyWizard() {
  const { t } = useTranslation()
  const [state, dispatch] = useReducer(wizardReducer, INITIAL_WIZARD_STATE)

  const {
    step, rawNote, noteRecord, selectedAlter, session, score, scorePath,
    loading, error, message, editEnabled, editRecord, correctionNote,
    reviewNote, dialogueSummary, primaryNextCorrection, supportingAction1,
    supportingAction2, directionAlignment, executionConsistency, avoidanceLevel,
    oneActionEvidence, oneAvoidanceEvidence, oneNextCorrection, verdictLabel,
    verdictSentence, assistantHelp, assistantSuggestion, assistantStatus,
    assistantLiveConfirmation, assistantLoading, assistantError, alterOptions,
  } = state

  useEffect(() => {
    fetchJson('/alter-dialogue/alters')
      .then((res: unknown) => {
        const data = res as { alters?: { alter_id: string }[] }
        if (data.alters && data.alters.length > 0) {
          dispatch({ type: 'SET_ALTER_OPTIONS', value: data.alters.map(a => ({ id: a.alter_id, name: a.alter_id })) })
        }
      })
      .catch(() => {})
  }, [])

  const run = async (label: string, task: () => Promise<void>) => {
    dispatch({ type: 'SET_LOADING', value: label })
    dispatch({ type: 'SET_ERROR', value: '' })
    dispatch({ type: 'SET_MESSAGE', value: '' })
    try {
      await task()
    } catch (e) {
      dispatch({ type: 'SET_ERROR', value: e instanceof Error ? e.message : t('weeklyReview.unknownError') })
    } finally {
      dispatch({ type: 'SET_LOADING', value: '' })
    }
  }

  const ingest = () => run('ingesting', async () => {
    const result = await ingestWeeklyNote(rawNote)
    dispatch({ type: 'INGEST_COMPLETE', record: result.record, message: `${t('weeklyReview.savedNote')} ${result.record.record_id}` })
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
    dispatch({ type: 'SAVE_EDIT_COMPLETE', record: result.record, message: t('weeklyReview.fieldsUpdated') })
  })

  const startReviewAction = () => run('starting review', async () => {
    if (!noteRecord) return
    const result = await startWeeklyReview(noteRecord.record_id, selectedAlter || null)
    dispatch({ type: 'START_REVIEW_COMPLETE', session: result.session, message: `${t('weeklyReview.reviewStarted')} ${result.session.session_id}` })
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
    dispatch({
      type: 'COMPLETE_REVIEW_COMPLETE',
      session: result.session,
      correction: result.session.next_week_primary_correction || primaryNextCorrection,
      message: t('weeklyReview.reviewCompleted'),
    })
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
    dispatch({
      type: 'SUBMIT_SCORE_COMPLETE',
      score: result.score,
      scorePath: result.score_path ?? null,
      message: `${t('weeklyReview.alignmentSaved')} ${result.score.score_id}`,
    })
  })

  const reset = () => dispatch({ type: 'RESET' })

  const loadAssistantStatus = async () => {
    try {
      const s = await fetchWeeklyReviewAssistantStatus()
      dispatch({ type: 'SET_ASSISTANT_STATUS', value: s })
    } catch {
      dispatch({ type: 'SET_ASSISTANT_STATUS', value: { provider_mode: 'disabled', configured: false } })
    }
  }

  const generateSuggestion = (live: boolean) => run('generating suggestion', async () => {
    dispatch({ type: 'SET_ASSISTANT_ERROR', value: '' })
    dispatch({ type: 'SET_ASSISTANT_SUGGESTION', value: '' })
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
      dispatch({ type: 'SET_ASSISTANT_SUGGESTION', value: result.suggestion })
    } else {
      dispatch({ type: 'SET_ASSISTANT_ERROR', value: result.message })
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
            onClick={() => dispatch({ type: 'SET_STEP', step: n as 1|2|3|4|5|6 })}
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
          setRawNote={v => dispatch({ type: 'SET_RAW_NOTE', value: v })}
          noteRecord={noteRecord}
          loading={loading}
          onIngest={ingest}
        />
      )}

      {step === 2 && noteRecord && editRecord && (
        <StepNoteEdit
          noteRecord={noteRecord}
          editRecord={editRecord}
          setEditRecord={v => dispatch({ type: 'SET_EDIT_RECORD', value: v })}
          editEnabled={editEnabled}
          setEditEnabled={v => dispatch({ type: 'SET_EDIT_ENABLED', value: v })}
          correctionNote={correctionNote}
          setCorrectionNote={v => dispatch({ type: 'SET_CORRECTION_NOTE', value: v })}
          loading={loading}
          onSaveEdit={saveEdit}
          onContinue={() => dispatch({ type: 'SET_STEP', step: 3 })}
        />
      )}

      {step === 3 && noteRecord && (
        <StepReview
          selectedAlter={selectedAlter}
          setSelectedAlter={v => dispatch({ type: 'SET_SELECTED_ALTER', value: v })}
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
          setReviewNote={v => dispatch({ type: 'SET_REVIEW_NOTE', value: v })}
          dialogueSummary={dialogueSummary}
          setDialogueSummary={v => dispatch({ type: 'SET_DIALOGUE_SUMMARY', value: v })}
          primaryNextCorrection={primaryNextCorrection}
          setPrimaryNextCorrection={v => dispatch({ type: 'SET_PRIMARY_NEXT_CORRECTION', value: v })}
          supportingAction1={supportingAction1}
          setSupportingAction1={v => dispatch({ type: 'SET_SUPPORTING_ACTION_1', value: v })}
          supportingAction2={supportingAction2}
          setSupportingAction2={v => dispatch({ type: 'SET_SUPPORTING_ACTION_2', value: v })}
          assistantHelp={assistantHelp}
          setAssistantHelp={v => dispatch({ type: 'SET_ASSISTANT_HELP', value: v })}
          assistantSuggestion={assistantSuggestion}
          assistantStatus={assistantStatus}
          assistantLiveConfirmation={assistantLiveConfirmation}
          setAssistantLiveConfirmation={v => dispatch({ type: 'SET_ASSISTANT_LIVE_CONFIRMATION', value: v })}
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
          setDirectionAlignment={v => dispatch({ type: 'SET_DIRECTION_ALIGNMENT', value: v })}
          executionConsistency={executionConsistency}
          setExecutionConsistency={v => dispatch({ type: 'SET_EXECUTION_CONSISTENCY', value: v })}
          avoidanceLevel={avoidanceLevel}
          setAvoidanceLevel={v => dispatch({ type: 'SET_AVOIDANCE_LEVEL', value: v })}
          oneActionEvidence={oneActionEvidence}
          setOneActionEvidence={v => dispatch({ type: 'SET_ONE_ACTION_EVIDENCE', value: v })}
          oneAvoidanceEvidence={oneAvoidanceEvidence}
          setOneAvoidanceEvidence={v => dispatch({ type: 'SET_ONE_AVOIDANCE_EVIDENCE', value: v })}
          oneNextCorrection={oneNextCorrection}
          setOneNextCorrection={v => dispatch({ type: 'SET_ONE_NEXT_CORRECTION', value: v })}
          verdictLabel={verdictLabel}
          setVerdictLabel={v => dispatch({ type: 'SET_VERDICT_LABEL', value: v })}
          verdictSentence={verdictSentence}
          setVerdictSentence={v => dispatch({ type: 'SET_VERDICT_SENTENCE', value: v })}
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
