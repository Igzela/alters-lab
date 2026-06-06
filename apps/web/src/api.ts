import type { ActionAlignmentScore, VerdictLabel, WeeklyNoteRecord, WeeklyReviewSession } from './types'

const API_BASE = ''

export class ApiError extends Error {
  constructor(
    public status: number,
    public errorCode: string,
    message: string,
    public requestId?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    let errorCode = 'UNKNOWN_ERROR'
    let message = `Request failed (${res.status})`
    let requestId: string | undefined
    try {
      const body = await res.json()
      errorCode = body.error || errorCode
      message = body.message || message
      requestId = body.request_id
    } catch {
      // non-JSON error response
    }
    throw new ApiError(res.status, errorCode, message, requestId)
  }
  return res.json()
}

export async function fetchJson(path: string) {
  const res = await fetch(`${API_BASE}${path}`)
  return handleResponse(res)
}

export async function postJson(path: string, body: unknown) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse(res)
}

export async function deleteJson(path: string, body: unknown) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse(res)
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
    behavior_validated: boolean
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

// --- Trend Analysis ---
export async function analyzeTrend(body: { lookback_weeks?: number; forecast_weeks?: number }) {
  return postJson('/trend-analysis/analyze', body) as Promise<{
    status: string
    overall_direction: string
    dimensions: Array<{
      dimension: string
      direction: string
      slope: number
      r_squared: number
      confidence_level: string
      data_points: number
    }>
    forecast: Array<{
      week_offset: number
      predicted_score: number
      lower_bound: number
      upper_bound: number
    }>
    confidence_interval: {
      level: string
      data_count: number
      consistency_score: number
      description: string
    }
    generated_at: string
  }>
}

// --- Dynamic Weight ---
export async function computeDynamicWeights(body: { lookback_weeks?: number }) {
  return postJson('/dynamic-weight/compute', body) as Promise<{
    status: string
    weights: Array<{
      dimension: string
      weight: number
      rationale: string
    }>
    overall_alignment: number
    recommendation: string
    generated_at: string
  }>
}

// --- Pattern Adjustment ---
export async function adjustForecast(body: { lookback_weeks?: number; forecast_weeks?: number }) {
  return postJson('/pattern-adjustment/adjust', body) as Promise<{
    status: string
    has_patterns: boolean
    original_forecast: Array<{
      week_offset: number
      predicted_score: number
      lower_bound: number
      upper_bound: number
    }>
    adjusted_forecast: Array<{
      week_offset: number
      original_score: number
      adjusted_score: number
      adjustment_delta: number
      adjustment_reason: string
      lower_bound: number
      upper_bound: number
    }>
    adjustments_applied: string[]
    generated_at: string
  }>
}

// --- Calibration Conversation ---
export async function startCalibrationConversation(body?: { branch_id?: string }) {
  return postJson('/calibration-conversation/start', body ?? {}) as Promise<{
    status: string
    conversation: {
      conversation_id: string
      status: string
      messages: Array<{ role: string; content: string; timestamp: string }>
      draft_ids: string[]
    }
  }>
}

export async function sendCalibrationMessage(conversationId: string, message: string) {
  return postJson(`/calibration-conversation/${conversationId}/message`, { message }) as Promise<{
    status: string
    conversation: {
      conversation_id: string
      status: string
      messages: Array<{ role: string; content: string; timestamp: string }>
      draft_ids: string[]
    }
    draft: {
      draft_id: string
      status: string
      conversation_id: string
      behavior_metrics: Record<string, unknown> | null
      rubric_scores: Record<string, unknown> | null
      external_evidence: Array<Record<string, unknown>>
      extraction_confidence: string
      llm_reasoning: string
    } | null
  }>
}

export async function getCalibrationConversation(conversationId: string) {
  return fetchJson(`/calibration-conversation/${conversationId}`) as Promise<{
    conversation: {
      conversation_id: string
      status: string
      messages: Array<{ role: string; content: string; timestamp: string }>
      draft_ids: string[]
    }
  }>
}

export async function getCalibrationDrafts(status?: string) {
  const qs = status ? `?status=${status}` : ''
  return fetchJson(`/calibration-conversation/drafts${qs}`) as Promise<{
    drafts: Array<{
      draft_id: string
      status: string
      conversation_id: string
      behavior_metrics: Record<string, unknown> | null
      rubric_scores: Record<string, unknown> | null
      external_evidence: Array<Record<string, unknown>>
      extraction_confidence: string
      llm_reasoning: string
    }>
    count: number
  }>
}

export async function confirmCalibrationDraft(draftId: string, corrections?: Record<string, unknown>) {
  return postJson(`/calibration-conversation/drafts/${draftId}/confirm`, { corrections: corrections ?? {} }) as Promise<{
    status: string
    draft: Record<string, unknown>
    records_written: string[]
  }>
}

export async function rejectCalibrationDraft(draftId: string) {
  return postJson(`/calibration-conversation/drafts/${draftId}/reject`, {}) as Promise<{
    status: string
    draft: Record<string, unknown>
  }>
}
