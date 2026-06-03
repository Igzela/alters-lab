import type { ActionAlignmentScore, VerdictLabel, WeeklyNoteRecord, WeeklyReviewSession } from '../../types'
import type { AlterOption, Step } from './types'

export type WizardState = {
  step: Step
  rawNote: string
  noteRecord: WeeklyNoteRecord | null
  selectedAlter: string
  session: WeeklyReviewSession | null
  score: ActionAlignmentScore | null
  scorePath: string | null
  loading: string
  error: string
  message: string
  editEnabled: boolean
  editRecord: WeeklyNoteRecord | null
  correctionNote: string
  reviewNote: string
  dialogueSummary: string
  primaryNextCorrection: string
  supportingAction1: string
  supportingAction2: string
  directionAlignment: number
  executionConsistency: number
  avoidanceLevel: number
  oneActionEvidence: string
  oneAvoidanceEvidence: string
  oneNextCorrection: string
  verdictLabel: VerdictLabel
  verdictSentence: string
  assistantHelp: string
  assistantSuggestion: string
  assistantStatus: { provider_mode: string; configured: boolean } | null
  assistantLiveConfirmation: string
  assistantLoading: boolean
  assistantError: string
  alterOptions: AlterOption[]
}

export type WizardAction =
  | { type: 'SET_STEP'; step: Step }
  | { type: 'SET_RAW_NOTE'; value: string }
  | { type: 'SET_SELECTED_ALTER'; value: string }
  | { type: 'SET_LOADING'; value: string }
  | { type: 'SET_ERROR'; value: string }
  | { type: 'SET_MESSAGE'; value: string }
  | { type: 'SET_EDIT_ENABLED'; value: boolean }
  | { type: 'SET_EDIT_RECORD'; value: WeeklyNoteRecord | null }
  | { type: 'SET_CORRECTION_NOTE'; value: string }
  | { type: 'SET_REVIEW_NOTE'; value: string }
  | { type: 'SET_DIALOGUE_SUMMARY'; value: string }
  | { type: 'SET_PRIMARY_NEXT_CORRECTION'; value: string }
  | { type: 'SET_SUPPORTING_ACTION_1'; value: string }
  | { type: 'SET_SUPPORTING_ACTION_2'; value: string }
  | { type: 'SET_DIRECTION_ALIGNMENT'; value: number }
  | { type: 'SET_EXECUTION_CONSISTENCY'; value: number }
  | { type: 'SET_AVOIDANCE_LEVEL'; value: number }
  | { type: 'SET_ONE_ACTION_EVIDENCE'; value: string }
  | { type: 'SET_ONE_AVOIDANCE_EVIDENCE'; value: string }
  | { type: 'SET_ONE_NEXT_CORRECTION'; value: string }
  | { type: 'SET_VERDICT_LABEL'; value: VerdictLabel }
  | { type: 'SET_VERDICT_SENTENCE'; value: string }
  | { type: 'SET_ASSISTANT_HELP'; value: string }
  | { type: 'SET_ASSISTANT_SUGGESTION'; value: string }
  | { type: 'SET_ASSISTANT_STATUS'; value: { provider_mode: string; configured: boolean } | null }
  | { type: 'SET_ASSISTANT_LIVE_CONFIRMATION'; value: string }
  | { type: 'SET_ASSISTANT_LOADING'; value: boolean }
  | { type: 'SET_ASSISTANT_ERROR'; value: string }
  | { type: 'SET_ALTER_OPTIONS'; value: AlterOption[] }
  | { type: 'INGEST_COMPLETE'; record: WeeklyNoteRecord; message: string }
  | { type: 'SAVE_EDIT_COMPLETE'; record: WeeklyNoteRecord; message: string }
  | { type: 'START_REVIEW_COMPLETE'; session: WeeklyReviewSession; message: string }
  | { type: 'COMPLETE_REVIEW_COMPLETE'; session: WeeklyReviewSession; correction: string; message: string }
  | { type: 'SUBMIT_SCORE_COMPLETE'; score: ActionAlignmentScore; scorePath: string; message: string }
  | { type: 'RESET' }

export const INITIAL_WIZARD_STATE: WizardState = {
  step: 1,
  rawNote: '',
  noteRecord: null,
  selectedAlter: '',
  session: null,
  score: null,
  scorePath: null,
  loading: '',
  error: '',
  message: '',
  editEnabled: false,
  editRecord: null,
  correctionNote: '',
  reviewNote: '',
  dialogueSummary: '',
  primaryNextCorrection: '',
  supportingAction1: '',
  supportingAction2: '',
  directionAlignment: 0.5,
  executionConsistency: 0.5,
  avoidanceLevel: 0.5,
  oneActionEvidence: '',
  oneAvoidanceEvidence: '',
  oneNextCorrection: '',
  verdictLabel: 'unstable_but_useful',
  verdictSentence: '',
  assistantHelp: 'general_review_suggestion',
  assistantSuggestion: '',
  assistantStatus: null,
  assistantLiveConfirmation: '',
  assistantLoading: false,
  assistantError: '',
  alterOptions: [
    { id: 'alter_A', name: 'alter_A' },
    { id: 'alter_B', name: 'alter_B' },
    { id: 'alter_C', name: 'alter_C' },
    { id: 'alter_D', name: 'alter_D' },
  ],
}

export function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, step: action.step }
    case 'SET_RAW_NOTE':
      return { ...state, rawNote: action.value }
    case 'SET_SELECTED_ALTER':
      return { ...state, selectedAlter: action.value }
    case 'SET_LOADING':
      return { ...state, loading: action.value }
    case 'SET_ERROR':
      return { ...state, error: action.value }
    case 'SET_MESSAGE':
      return { ...state, message: action.value }
    case 'SET_EDIT_ENABLED':
      return { ...state, editEnabled: action.value }
    case 'SET_EDIT_RECORD':
      return { ...state, editRecord: action.value }
    case 'SET_CORRECTION_NOTE':
      return { ...state, correctionNote: action.value }
    case 'SET_REVIEW_NOTE':
      return { ...state, reviewNote: action.value }
    case 'SET_DIALOGUE_SUMMARY':
      return { ...state, dialogueSummary: action.value }
    case 'SET_PRIMARY_NEXT_CORRECTION':
      return { ...state, primaryNextCorrection: action.value }
    case 'SET_SUPPORTING_ACTION_1':
      return { ...state, supportingAction1: action.value }
    case 'SET_SUPPORTING_ACTION_2':
      return { ...state, supportingAction2: action.value }
    case 'SET_DIRECTION_ALIGNMENT':
      return { ...state, directionAlignment: action.value }
    case 'SET_EXECUTION_CONSISTENCY':
      return { ...state, executionConsistency: action.value }
    case 'SET_AVOIDANCE_LEVEL':
      return { ...state, avoidanceLevel: action.value }
    case 'SET_ONE_ACTION_EVIDENCE':
      return { ...state, oneActionEvidence: action.value }
    case 'SET_ONE_AVOIDANCE_EVIDENCE':
      return { ...state, oneAvoidanceEvidence: action.value }
    case 'SET_ONE_NEXT_CORRECTION':
      return { ...state, oneNextCorrection: action.value }
    case 'SET_VERDICT_LABEL':
      return { ...state, verdictLabel: action.value }
    case 'SET_VERDICT_SENTENCE':
      return { ...state, verdictSentence: action.value }
    case 'SET_ASSISTANT_HELP':
      return { ...state, assistantHelp: action.value }
    case 'SET_ASSISTANT_SUGGESTION':
      return { ...state, assistantSuggestion: action.value }
    case 'SET_ASSISTANT_STATUS':
      return { ...state, assistantStatus: action.value }
    case 'SET_ASSISTANT_LIVE_CONFIRMATION':
      return { ...state, assistantLiveConfirmation: action.value }
    case 'SET_ASSISTANT_LOADING':
      return { ...state, assistantLoading: action.value }
    case 'SET_ASSISTANT_ERROR':
      return { ...state, assistantError: action.value }
    case 'SET_ALTER_OPTIONS':
      return { ...state, alterOptions: action.value }
    case 'INGEST_COMPLETE':
      return {
        ...state,
        noteRecord: action.record,
        editRecord: action.record,
        primaryNextCorrection: action.record.desired_correction,
        oneNextCorrection: action.record.desired_correction,
        message: action.message,
        step: 2,
      }
    case 'SAVE_EDIT_COMPLETE':
      return {
        ...state,
        noteRecord: action.record,
        editRecord: action.record,
        editEnabled: false,
        correctionNote: '',
        message: action.message,
      }
    case 'START_REVIEW_COMPLETE':
      return {
        ...state,
        session: action.session,
        message: action.message,
        step: 4,
      }
    case 'COMPLETE_REVIEW_COMPLETE':
      return {
        ...state,
        session: action.session,
        oneNextCorrection: action.correction,
        message: action.message,
        step: 5,
      }
    case 'SUBMIT_SCORE_COMPLETE':
      return {
        ...state,
        score: action.score,
        scorePath: action.scorePath,
        message: action.message,
        step: 6,
      }
    case 'RESET':
      return { ...INITIAL_WIZARD_STATE, alterOptions: state.alterOptions }
  }
}
