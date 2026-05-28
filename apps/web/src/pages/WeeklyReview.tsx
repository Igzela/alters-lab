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

const btn = 'px-3 py-2 text-sm bg-gray-800 text-white rounded border border-gray-700 hover:bg-gray-700 disabled:opacity-50'
const input = 'w-full px-2.5 py-2 border border-gray-600 rounded text-sm bg-gray-800 text-white'
const field = 'grid gap-1.5 mb-3'

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
      <h2 className="text-lg font-semibold">{t('weeklyReview.title')}</h2>
      <p className="text-gray-500 text-xs">{t('weeklyReview.description')}</p>
      <P6Progress />

      <div className="flex gap-2 flex-wrap mb-4">
        {[1, 2, 3, 4, 5, 6].map(n => (
          <button
            key={n}
            className={`${btn} ${step === n ? 'bg-gray-800 text-white' : 'bg-transparent text-gray-400 border border-gray-600 hover:text-white hover:bg-gray-800/50'}`}
            type="button"
            onClick={() => setStep(n as Step)}
            disabled={n > 1 && !noteRecord}
          >
            {t(`weeklyReview.step${n}`)}
          </button>
        ))}
      </div>

      {error && <p className="text-red-500 text-sm">{t('weeklyReview.error')} {error}</p>}
      {message && <p className="text-green-400 text-sm">{message}</p>}

      {step === 1 && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step1Title')}</h3>
          <button className={`${btn} mb-2.5`} type="button" onClick={() => setRawNote(NOTE_TEMPLATE)}>
            {t('weeklyReview.useTemplate')}
          </button>
          <textarea
            className={`${input} min-h-[280px] font-mono`}
            value={rawNote}
            onChange={e => setRawNote(e.target.value)}
            placeholder={NOTE_TEMPLATE}
          />
          <button className={`${btn} mt-2.5`} type="button" onClick={ingest} disabled={!!loading || !rawNote.trim()}>
            {loading === 'ingesting' ? t('weeklyReview.ingesting') : t('weeklyReview.ingestNote')}
          </button>
          {noteRecord && <p className="text-sm text-gray-400 mt-2">{t('weeklyReview.savedRecordId')} {noteRecord.record_id}</p>}
        </section>
      )}

      {step === 2 && noteRecord && editRecord && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step2Title')}</h3>
          <p className="text-sm text-gray-400 mb-2">{t('weeklyReview.rawNotePreserved')} {noteRecord.raw_note_preserved ? 'Yes' : 'No'}</p>
          <Field label="session_type" value={editRecord.session_type} editing={editEnabled} onChange={v => setEditRecord({ ...editRecord, session_type: v as WeeklyNoteRecord['session_type'] })} />
          <label className={field}>
            observable_facts
            {editEnabled ? (
              <textarea
                className={`${input} min-h-[100px]`}
                value={editRecord.observable_facts.join('\n')}
                onChange={e => setEditRecord({ ...editRecord, observable_facts: e.target.value.split('\n').map(v => v.trim()).filter(Boolean) })}
              />
            ) : (
              <ul className="text-sm text-gray-300">{noteRecord.observable_facts.map((fact, i) => <li key={i}>{fact}</li>)}</ul>
            )}
          </label>
          <Field label="subjective_state" value={editRecord.subjective_state} editing={editEnabled} onChange={v => setEditRecord({ ...editRecord, subjective_state: v })} />
          <Field label="primary_problem" value={editRecord.primary_problem} editing={editEnabled} onChange={v => setEditRecord({ ...editRecord, primary_problem: v })} />
          <Field label="friction_or_avoidance_point" value={editRecord.friction_or_avoidance_point} editing={editEnabled} onChange={v => setEditRecord({ ...editRecord, friction_or_avoidance_point: v })} />
          <Field label="desired_correction / primary correction" value={editRecord.desired_correction} editing={editEnabled} onChange={v => setEditRecord({ ...editRecord, desired_correction: v })} />
          {editEnabled && (
            <label className={field}>
              correction_note
              <input className={input} value={correctionNote} onChange={e => setCorrectionNote(e.target.value)} />
            </label>
          )}
          <div className="flex gap-2 flex-wrap">
            <button className={btn} type="button" onClick={() => setEditEnabled(!editEnabled)}>
              {editEnabled ? t('weeklyReview.cancelEdit') : t('weeklyReview.editFields')}
            </button>
            {editEnabled && <button className={btn} type="button" onClick={saveEdit} disabled={!!loading || !correctionNote.trim()}>{t('weeklyReview.saveEdit')}</button>}
            <button className={btn} type="button" onClick={() => setStep(3)}>{t('weeklyReview.continue')}</button>
          </div>
        </section>
      )}

      {step === 3 && noteRecord && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step3Title')}</h3>
          <label className={field}>
            {t('weeklyReview.selectAlter')}
            <select className={input} value={selectedAlter} onChange={e => setSelectedAlter(e.target.value)}>
              <option value="">{t('weeklyReview.systemRecommended')}</option>
              {alterOptions.map(a => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </label>
          <button className={btn} type="button" onClick={startReview} disabled={!!loading}>
            {loading === 'starting review' ? t('weeklyReview.starting') : t('weeklyReview.startReview')}
          </button>
          {session && <p className="text-sm text-gray-400 mt-2">{t('weeklyReview.sessionId')} {session.session_id}</p>}
        </section>
      )}

      {step === 4 && session && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step4Title')}</h3>
          <TextArea label={t('weeklyReview.reviewNote')} value={reviewNote} onChange={setReviewNote} />
          <TextArea label={t('weeklyReview.dialogueSummary')} value={dialogueSummary} onChange={setDialogueSummary} />
          <TextInput label={t('weeklyReview.primaryNextCorrection')} value={primaryNextCorrection} onChange={setPrimaryNextCorrection} />
          <TextInput label={t('weeklyReview.supportingAction1')} value={supportingAction1} onChange={setSupportingAction1} />
          <TextInput label={t('weeklyReview.supportingAction2')} value={supportingAction2} onChange={setSupportingAction2} />

          <div className="border border-gray-600 rounded-lg p-3.5 mb-4 bg-gray-800/30">
            <h4 className="text-sm font-medium mb-1.5">{t('weeklyReview.assistantSuggestion')}</h4>
            <p className="text-xs text-gray-400 mb-2">{t('weeklyReview.providerAdvisory')}</p>
            <label className={field}>
              {t('weeklyReview.requestedHelp')}
              <select className={input} value={assistantHelp} onChange={e => setAssistantHelp(e.target.value)}>
                <option value="general_review_suggestion">{t('weeklyReview.generalSuggestion')}</option>
                <option value="summarize_facts">{t('weeklyReview.summarizeFacts')}</option>
                <option value="identify_friction">{t('weeklyReview.identifyFriction')}</option>
                <option value="draft_primary_correction">{t('weeklyReview.draftCorrection')}</option>
                <option value="suggest_supporting_actions">{t('weeklyReview.suggestActions')}</option>
                <option value="challenge_avoidance">{t('weeklyReview.challengeAvoidance')}</option>
              </select>
            </label>
            <div className="flex gap-2 flex-wrap mb-2.5">
              <button className={btn} type="button" onClick={() => loadAssistantStatus()} disabled={assistantLoading}>
                {t('weeklyReview.checkProvider')}
              </button>
              <button className={btn} type="button" onClick={() => generateSuggestion(false)} disabled={!!loading || assistantLoading}>
                {loading === 'generating suggestion' ? t('weeklyReview.generating') : t('weeklyReview.generateDryRun')}
              </button>
            </div>
            {assistantStatus && (
              <p className="text-xs text-gray-400">{t('weeklyReview.providerMode')} {assistantStatus.provider_mode} | {t('provider.configured')} {assistantStatus.configured ? 'yes' : 'no'}</p>
            )}
            {assistantStatus?.configured && assistantStatus.provider_mode === 'openai-compatible-http' && (
              <div className="mt-2">
                <label className="grid gap-1.5 mb-2">
                  {t('weeklyReview.liveConfirmation')}
                  <input className={input} value={assistantLiveConfirmation} onChange={e => setAssistantLiveConfirmation(e.target.value)} placeholder="run-live-weekly-review-assistant" />
                </label>
                <button className={btn} type="button" onClick={() => generateSuggestion(true)} disabled={!!loading || assistantLoading || assistantLiveConfirmation !== 'run-live-weekly-review-assistant'}>
                  {t('weeklyReview.generateLive')}
                </button>
              </div>
            )}
            {assistantError && <p className="text-red-500 text-sm mt-2">{assistantError}</p>}
            {assistantSuggestion && (
              <div className="mt-2.5 p-2.5 border border-gray-600 rounded bg-white">
                <p className="text-xs font-semibold text-gray-400 mb-1.5">{t('weeklyReview.unverifiedSuggestion')}</p>
                <pre className="whitespace-pre-wrap text-sm text-gray-800 m-0">{assistantSuggestion}</pre>
                <div className="flex gap-2 mt-2 flex-wrap">
                  <button className={`${btn} bg-gray-500 hover:bg-gray-400`} type="button" onClick={() => setReviewNote(assistantSuggestion)}>
                    {t('weeklyReview.copyToReviewNote')}
                  </button>
                  <button className={`${btn} bg-gray-500 hover:bg-gray-400`} type="button" onClick={() => setDialogueSummary(assistantSuggestion)}>
                    {t('weeklyReview.copyToDialogue')}
                  </button>
                  <button className={`${btn} bg-gray-500 hover:bg-gray-400`} type="button" onClick={() => setPrimaryNextCorrection(assistantSuggestion)}>
                    {t('weeklyReview.copyToCorrection')}
                  </button>
                </div>
              </div>
            )}
          </div>

          <button className={btn} type="button" onClick={completeReview} disabled={!!loading || !reviewNote.trim() || !primaryNextCorrection.trim()}>
            {loading === 'completing review' ? t('weeklyReview.completing') : t('weeklyReview.completeReview')}
          </button>
          {session.status === 'completed' && (
            <div className="mt-2 text-sm text-gray-300">
              <p>{t('weeklyReview.statusCompleted')}</p>
              <p>{t('weeklyReview.nextCorrection')} {session.next_week_primary_correction}</p>
              <p>{t('weeklyReview.supportingActions')} {session.supporting_actions.join(', ') || t('weeklyReview.none')}</p>
            </div>
          )}
        </section>
      )}

      {step === 5 && session && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step5Title')}</h3>
          <Slider label={t('weeklyReview.directionQuestion')} value={directionAlignment} onChange={setDirectionAlignment} />
          <Slider label={t('weeklyReview.consistencyQuestion')} value={executionConsistency} onChange={setExecutionConsistency} />
          <Slider label={t('weeklyReview.avoidanceQuestion')} value={avoidanceLevel} onChange={setAvoidanceLevel} />
          <TextInput label={t('weeklyReview.actionEvidence')} value={oneActionEvidence} onChange={setOneActionEvidence} />
          <TextInput label={t('weeklyReview.avoidanceEvidence')} value={oneAvoidanceEvidence} onChange={setOneAvoidanceEvidence} />
          <TextInput label={t('weeklyReview.nextCorrectionEvidence')} value={oneNextCorrection} onChange={setOneNextCorrection} />
          <label className={field}>
            {t('weeklyReview.verdictLabel')}
            <select className={input} value={verdictLabel} onChange={e => setVerdictLabel(e.target.value as VerdictLabel)}>
              {verdicts.map(v => <option key={v} value={v}>{v.replace(/_/g, ' ')}</option>)}
            </select>
            <span className="text-sm text-gray-400 mt-0.5">{VERDICT_DESCRIPTIONS[verdictLabel]}</span>
          </label>
          <TextInput label={t('weeklyReview.verdictSentence')} value={verdictSentence} onChange={setVerdictSentence} />
          <button
            className={btn}
            type="button"
            onClick={submitScore}
            disabled={!!loading || !oneActionEvidence.trim() || !oneAvoidanceEvidence.trim() || !oneNextCorrection.trim() || !verdictSentence.trim()}
          >
            {loading === 'saving score' ? t('weeklyReview.saving') : t('weeklyReview.saveAlignment')}
          </button>
          {score && (
            <div className="mt-2 text-sm text-gray-300">
              <p>{t('weeklyReview.scoreId')} {score.score_id}</p>
              <p>{t('weeklyReview.alignmentScore')} {score.action_alignment_score}</p>
              {scorePath && <p>{t('weeklyReview.savedPath')} {scorePath}</p>}
            </div>
          )}
        </section>
      )}

      {step === 6 && noteRecord && session && score && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step6Title')}</h3>
          <div className="text-sm text-gray-300 space-y-1">
            <p>{t('weeklyReview.noteRecordId')} {noteRecord.record_id}</p>
            <p>{t('weeklyReview.reviewSessionId')} {session.session_id}</p>
            <p>{t('weeklyReview.scoreRecordId')} {score.score_id}</p>
            <p>{t('weeklyReview.alignmentScore')} {score.action_alignment_score}</p>
            <p>{t('weeklyReview.p6Validated')}</p>
            <p>{t('weeklyReview.p6Sealed')}</p>
          </div>
          <p className="text-xs text-gray-400 mt-2">{t('weeklyReview.weekEvidenceNote')}</p>
          <button className={`${btn} mt-2.5`} type="button" onClick={reset}>{t('weeklyReview.resetFlow')}</button>
        </section>
      )}
    </div>
  )
}

function Field({ label, value, editing, onChange }: { label: string; value: string; editing: boolean; onChange: (value: string) => void }) {
  return (
    <label className={field}>
      <span className="text-sm text-gray-300">{label}</span>
      {editing ? <input className={input} value={value} onChange={e => onChange(e.target.value)} /> : <span className="text-sm text-gray-300">{value}</span>}
    </label>
  )
}

function TextInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className={field}>
      <span className="text-sm text-gray-300">{label}</span>
      <input className={input} value={value} onChange={e => onChange(e.target.value)} />
    </label>
  )
}

function TextArea({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className={field}>
      <span className="text-sm text-gray-300">{label}</span>
      <textarea className={`${input} min-h-[80px]`} value={value} onChange={e => onChange(e.target.value)} />
    </label>
  )
}

function Slider({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <label className="grid gap-1.5 mb-3">
      <span className="text-sm text-gray-300">{label}</span>
      <div className="flex items-center gap-2.5">
        <input className="flex-1" type="range" min={0} max={1} step={0.05} value={value} onChange={e => onChange(Number(e.target.value))} />
        <input className={`${input} max-w-[120px]`} type="number" min={0} max={1} step={0.05} value={value} onChange={e => onChange(Number(e.target.value))} />
      </div>
    </label>
  )
}
