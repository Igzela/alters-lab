import type { ActionAlignmentScore, VerdictLabel, WeeklyNoteRecord, WeeklyReviewSession } from './types'

const API_BASE = ''

export async function fetchJson(path: string) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`${path}: ${res.status}`)
  return res.json()
}

export async function postJson(path: string, body: unknown) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${path}: ${res.status}`)
  return res.json()
}

export async function deleteJson(path: string, body: unknown) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${path}: ${res.status}`)
  return res.json()
}

export async function ingestWeeklyNote(raw_note: string) {
  return postJson('/obsidian-weekly-note/ingest', { raw_note, save: true }) as Promise<{
    status: string
    record: WeeklyNoteRecord
    record_path: string | null
  }>
}

export async function editWeeklyNote(recordId: string, body: Partial<WeeklyNoteRecord> & { correction_note: string }) {
  return postJson(`/obsidian-weekly-note/${recordId}/edit`, body) as Promise<{
    status: string
    record: WeeklyNoteRecord
    record_path: string | null
  }>
}

export async function listWeeklyNotes() {
  return fetchJson('/obsidian-weekly-note/list') as Promise<{ status: string; records: WeeklyNoteRecord[]; count: number }>
}

export async function startWeeklyReview(weekly_note_record_id: string, selected_alter_id: string | null) {
  return postJson('/weekly-review/start', {
    weekly_note_record_id,
    selected_alter_id: selected_alter_id || null,
  }) as Promise<{ status: string; session: WeeklyReviewSession; session_path: string | null }>
}

export async function completeWeeklyReview(
  sessionId: string,
  body: {
    review_note: string
    dialogue_summary: string
    primary_next_correction: string
    supporting_actions: string[]
  },
) {
  return postJson(`/weekly-review/${sessionId}/complete`, body) as Promise<{
    status: string
    session: WeeklyReviewSession
    session_path: string | null
  }>
}

export async function listWeeklyReviews() {
  return fetchJson('/weekly-review/list') as Promise<{ status: string; sessions: WeeklyReviewSession[]; count: number }>
}

export async function scoreActionAlignment(body: {
  session_id: string
  scores: {
    direction_alignment: number
    execution_consistency: number
    avoidance_level: number
  }
  evidence: {
    one_action_evidence: string
    one_avoidance_or_friction_evidence: string
    one_next_correction: string
  }
  verdict_label: VerdictLabel
  verdict_sentence: string
  save: boolean
}) {
  return postJson('/action-alignment/score', body) as Promise<{
    status: string
    score: ActionAlignmentScore
    score_path: string | null
  }>
}

export async function listActionAlignmentScores() {
  return fetchJson('/action-alignment/list') as Promise<{ status: string; scores: ActionAlignmentScore[]; count: number }>
}

export async function fetchWeeklyReviewAssistantStatus() {
  return fetchJson('/weekly-review-assistant/status') as Promise<{
    provider_mode: string
    configured: boolean
    p6_behavior_validated: boolean
    p6_sealed: boolean
  }>
}

export async function suggestWeeklyReviewAssistant(body: {
  weekly_note_record_id?: string | null
  weekly_review_session_id?: string | null
  raw_note_excerpt?: string | null
  review_context?: string | null
  requested_help?: string
  dry_run?: boolean
  live_generation?: boolean
  confirmation?: string | null
}) {
  return postJson('/weekly-review-assistant/suggest', body) as Promise<{
    status: string
    configured: boolean
    suggestion: string | null
    suggestion_label: string
    provider_mode: string
    dry_run: boolean
    live_generation: boolean
    network_call_made: boolean
    message: string
  }>
}
