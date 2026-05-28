import { useState, useEffect } from 'react'
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
      setError(e instanceof Error ? e.message : 'Unknown error')
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
    setMessage(`Saved weekly note ${result.record.record_id}`)
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
    setMessage('Extracted fields updated from explicit correction.')
  })

  const startReview = () => run('starting review', async () => {
    if (!noteRecord) return
    const result = await startWeeklyReview(noteRecord.record_id, selectedAlter || null)
    setSession(result.session)
    setMessage(`Started review ${result.session.session_id}`)
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
    setMessage('Review completed.')
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
    setMessage(`Action alignment saved ${result.score.score_id}`)
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
      <h2 className="text-lg font-semibold">Weekly Review</h2>
      <p className="text-gray-500 text-xs">This is the primary P6 weekly review entry point. Records created here are week evidence, not P6 validation.</p>
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
            Step {n}
          </button>
        ))}
      </div>

      {error && <p className="text-red-500 text-sm">Error: {error}</p>}
      {message && <p className="text-green-400 text-sm">{message}</p>}

      {step === 1 && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">Step 1: Paste Weekly Note</h3>
          <button className={`${btn} mb-2.5`} type="button" onClick={() => setRawNote(NOTE_TEMPLATE)}>
            Use template
          </button>
          <textarea
            className={`${input} min-h-[280px] font-mono`}
            value={rawNote}
            onChange={e => setRawNote(e.target.value)}
            placeholder={NOTE_TEMPLATE}
          />
          <button className={`${btn} mt-2.5`} type="button" onClick={ingest} disabled={!!loading || !rawNote.trim()}>
            {loading === 'ingesting' ? 'Ingesting...' : 'Ingest note'}
          </button>
          {noteRecord && <p className="text-sm text-gray-400 mt-2">Saved weekly_note_record_id: {noteRecord.record_id}</p>}
        </section>
      )}

      {step === 2 && noteRecord && editRecord && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">Step 2: Review Extracted Record</h3>
          <p className="text-sm text-gray-400 mb-2">Raw note preserved: {noteRecord.raw_note_preserved ? 'Yes' : 'No'}</p>
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
              {editEnabled ? 'Cancel edit' : 'Edit extracted fields'}
            </button>
            {editEnabled && <button className={btn} type="button" onClick={saveEdit} disabled={!!loading || !correctionNote.trim()}>Save edit</button>}
            <button className={btn} type="button" onClick={() => setStep(3)}>Continue</button>
          </div>
        </section>
      )}

      {step === 3 && noteRecord && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">Step 3: Start Review Session</h3>
          <label className={field}>
            Select alter
            <select className={input} value={selectedAlter} onChange={e => setSelectedAlter(e.target.value)}>
              <option value="">system recommended / blank</option>
              {alterOptions.map(a => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </label>
          <button className={btn} type="button" onClick={startReview} disabled={!!loading}>
            {loading === 'starting review' ? 'Starting...' : 'Start review'}
          </button>
          {session && <p className="text-sm text-gray-400 mt-2">weekly_review_session_id: {session.session_id}</p>}
        </section>
      )}

      {step === 4 && session && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">Step 4: Complete Review</h3>
          <TextArea label="review_note" value={reviewNote} onChange={setReviewNote} />
          <TextArea label="dialogue_summary optional" value={dialogueSummary} onChange={setDialogueSummary} />
          <TextInput label="primary_next_correction" value={primaryNextCorrection} onChange={setPrimaryNextCorrection} />
          <TextInput label="supporting_action_1 optional" value={supportingAction1} onChange={setSupportingAction1} />
          <TextInput label="supporting_action_2 optional" value={supportingAction2} onChange={setSupportingAction2} />

          <div className="border border-gray-600 rounded-lg p-3.5 mb-4 bg-gray-800/30">
            <h4 className="text-sm font-medium mb-1.5">Assistant Suggestion</h4>
            <p className="text-xs text-gray-400 mb-2">Provider output is advisory and unverified. You must manually copy/edit anything that becomes part of the review.</p>
            <label className={field}>
              Requested help
              <select className={input} value={assistantHelp} onChange={e => setAssistantHelp(e.target.value)}>
                <option value="general_review_suggestion">General review suggestion</option>
                <option value="summarize_facts">Summarize facts</option>
                <option value="identify_friction">Identify friction</option>
                <option value="draft_primary_correction">Draft primary correction</option>
                <option value="suggest_supporting_actions">Suggest supporting actions</option>
                <option value="challenge_avoidance">Challenge avoidance</option>
              </select>
            </label>
            <div className="flex gap-2 flex-wrap mb-2.5">
              <button className={btn} type="button" onClick={() => loadAssistantStatus()} disabled={assistantLoading}>
                Check provider status
              </button>
              <button className={btn} type="button" onClick={() => generateSuggestion(false)} disabled={!!loading || assistantLoading}>
                {loading === 'generating suggestion' ? 'Generating...' : 'Generate dry-run suggestion'}
              </button>
            </div>
            {assistantStatus && (
              <p className="text-xs text-gray-400">Provider mode: {assistantStatus.provider_mode} | Configured: {assistantStatus.configured ? 'yes' : 'no'}</p>
            )}
            {assistantStatus?.configured && assistantStatus.provider_mode === 'openai-compatible-http' && (
              <div className="mt-2">
                <label className="grid gap-1.5 mb-2">
                  Live confirmation
                  <input className={input} value={assistantLiveConfirmation} onChange={e => setAssistantLiveConfirmation(e.target.value)} placeholder="run-live-weekly-review-assistant" />
                </label>
                <button className={btn} type="button" onClick={() => generateSuggestion(true)} disabled={!!loading || assistantLoading || assistantLiveConfirmation !== 'run-live-weekly-review-assistant'}>
                  Generate live provider suggestion
                </button>
              </div>
            )}
            {assistantError && <p className="text-red-500 text-sm mt-2">{assistantError}</p>}
            {assistantSuggestion && (
              <div className="mt-2.5 p-2.5 border border-gray-600 rounded bg-white">
                <p className="text-xs font-semibold text-gray-400 mb-1.5">Unverified provider suggestion</p>
                <pre className="whitespace-pre-wrap text-sm text-gray-800 m-0">{assistantSuggestion}</pre>
                <div className="flex gap-2 mt-2 flex-wrap">
                  <button className={`${btn} bg-gray-500 hover:bg-gray-400`} type="button" onClick={() => setReviewNote(assistantSuggestion)}>
                    Copy to review_note
                  </button>
                  <button className={`${btn} bg-gray-500 hover:bg-gray-400`} type="button" onClick={() => setDialogueSummary(assistantSuggestion)}>
                    Copy to dialogue_summary
                  </button>
                  <button className={`${btn} bg-gray-500 hover:bg-gray-400`} type="button" onClick={() => setPrimaryNextCorrection(assistantSuggestion)}>
                    Copy to primary_next_correction
                  </button>
                </div>
              </div>
            )}
          </div>

          <button className={btn} type="button" onClick={completeReview} disabled={!!loading || !reviewNote.trim() || !primaryNextCorrection.trim()}>
            {loading === 'completing review' ? 'Completing...' : 'Complete review'}
          </button>
          {session.status === 'completed' && (
            <div className="mt-2 text-sm text-gray-300">
              <p>Status: completed</p>
              <p>next_week_primary_correction: {session.next_week_primary_correction}</p>
              <p>supporting_actions: {session.supporting_actions.join(', ') || 'none'}</p>
            </div>
          )}
        </section>
      )}

      {step === 5 && session && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">Step 5: Action Alignment Score</h3>
          <Slider label="Did my actions match my endorsed direction?" value={directionAlignment} onChange={setDirectionAlignment} />
          <Slider label="Did I actually execute consistently?" value={executionConsistency} onChange={setExecutionConsistency} />
          <Slider label="How much avoidance/friction was present? Higher means more avoidance." value={avoidanceLevel} onChange={setAvoidanceLevel} />
          <TextInput label="one_action_evidence" value={oneActionEvidence} onChange={setOneActionEvidence} />
          <TextInput label="one_avoidance_or_friction_evidence" value={oneAvoidanceEvidence} onChange={setOneAvoidanceEvidence} />
          <TextInput label="one_next_correction" value={oneNextCorrection} onChange={setOneNextCorrection} />
          <label className={field}>
            verdict_label
            <select className={input} value={verdictLabel} onChange={e => setVerdictLabel(e.target.value as VerdictLabel)}>
              {verdicts.map(v => <option key={v} value={v}>{v.replace(/_/g, ' ')}</option>)}
            </select>
            <span className="text-sm text-gray-400 mt-0.5">{VERDICT_DESCRIPTIONS[verdictLabel]}</span>
          </label>
          <TextInput label="verdict_sentence" value={verdictSentence} onChange={setVerdictSentence} />
          <button
            className={btn}
            type="button"
            onClick={submitScore}
            disabled={!!loading || !oneActionEvidence.trim() || !oneAvoidanceEvidence.trim() || !oneNextCorrection.trim() || !verdictSentence.trim()}
          >
            {loading === 'saving score' ? 'Saving...' : 'Save action alignment'}
          </button>
          {score && (
            <div className="mt-2 text-sm text-gray-300">
              <p>score_id / calibration_record_id: {score.score_id}</p>
              <p>action_alignment_score: {score.action_alignment_score}</p>
              {scorePath && <p>saved path: {scorePath}</p>}
            </div>
          )}
        </section>
      )}

      {step === 6 && noteRecord && session && score && (
        <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
          <h3 className="text-sm font-medium mb-2">Step 6: Completion Summary</h3>
          <div className="text-sm text-gray-300 space-y-1">
            <p>weekly_note_record_id: {noteRecord.record_id}</p>
            <p>weekly_review_session_id: {session.session_id}</p>
            <p>action_alignment_score_id: {score.score_id}</p>
            <p>action_alignment_score: {score.action_alignment_score}</p>
            <p>P6 behavior validated: false</p>
            <p>P6 sealed: false</p>
          </div>
          <p className="text-xs text-gray-400 mt-2">This is Week evidence, not P6 validation. P6 requires 4 real weekly reviews, 4 calibration records, and 1 pattern review across the validation window.</p>
          <button className={`${btn} mt-2.5`} type="button" onClick={reset}>Reset flow</button>
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
