import type { components } from './api-types'

// Re-export generated backend types (single source of truth)
export type ActionAlignmentScore = components['schemas']['ActionAlignmentScoreRecord']
export type WeeklyNoteRecord = components['schemas']['WeeklyNoteExtractedRecord']
export type WeeklyReviewSession = components['schemas']['WeeklyReviewSessionRecord']

// VerdictLabel inlined in generated types (Literal union), keep manual for convenience
export type VerdictLabel =
  | 'aligned_progress'
  | 'noisy_progress'
  | 'avoidance_disguised_as_work'
  | 'recovery_week'
  | 'unstable_but_useful'
  | 'blocked_by_environment'

// Frontend-only types (not in backend schema)
export type SessionType = 'personal' | 'project' | 'learning' | 'relationship'

export type Page =
  | 'dashboard'
  | 'status'
  | 'weekly'
  | 'dialogue'
  | 'reality'
  | 'history'
  | 'rubric'
  | 'checkpoint'
  | 'provider'
  | 'getting-started'
  | 'patterns'
  | 'validation'
  | 'data'
  | 'predictor-profile'
  | 'outcome-targets'
  | 'branch-forecast'
  | 'forecast-calibration'
  | 'public-priors'
  | 'calibration-conversation'

export const VALID_PAGES: Page[] = [
  'dashboard', 'status', 'weekly', 'dialogue', 'reality', 'history',
  'rubric', 'checkpoint', 'provider', 'getting-started', 'patterns',
  'validation', 'data', 'predictor-profile', 'outcome-targets',
  'branch-forecast', 'forecast-calibration', 'public-priors',
  'calibration-conversation',
]
