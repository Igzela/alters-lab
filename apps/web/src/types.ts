export type SessionType = 'personal' | 'project' | 'learning' | 'relationship'

export type WeeklyNoteRecord = {
  record_id: string
  raw_note_preserved: true
  derived_from_raw_note: true
  source_path: string | null
  raw_note: string
  session_type: SessionType
  observable_facts: string[]
  subjective_state: string
  primary_problem: string
  friction_or_avoidance_point: string
  desired_correction: string
  extraction_warnings: string[]
  created_at: string
  updated_at: string | null
}

export type WeeklyReviewSession = {
  session_id: string
  weekly_note_record_id: string
  session_type: SessionType
  status: 'started' | 'completed'
  selected_alter_id: string | null
  dialogue_summary: string
  review_note: string | null
  next_week_primary_correction: string | null
  supporting_actions: string[]
  created_at: string
  completed_at: string | null
}

export type VerdictLabel =
  | 'aligned_progress'
  | 'noisy_progress'
  | 'avoidance_disguised_as_work'
  | 'recovery_week'
  | 'unstable_but_useful'
  | 'blocked_by_environment'

export type ActionAlignmentScore = {
  score_id: string
  session_id: string
  action_alignment_score: number
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
  created_at: string
}

export type Page = 'dashboard' | 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started' | 'patterns' | 'validation' | 'data'

export const VALID_PAGES: Page[] = ['dashboard', 'status', 'weekly', 'dialogue', 'reality', 'history', 'rubric', 'checkpoint', 'provider', 'getting-started', 'patterns', 'validation', 'data']
