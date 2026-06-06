// Re-export all hooks from domain-specific files for backward compatibility.
// New code should import directly from the domain file instead.

export { useWeeklyNotes, useIngestWeeklyNote, useEditWeeklyNote } from './useWeeklyNoteHooks'
export { useWeeklyReviews, useStartWeeklyReview, useCompleteWeeklyReview, useWeeklyReviewAssistantStatus, useSuggestWeeklyReviewAssistant } from './useWeeklyReviewHooks'
export { useActionAlignmentScores, useScoreActionAlignment } from './useActionAlignmentHooks'
export { useProviderConfig, useUpdateProviderConfig, useProviderStatus, useStoreSecret, useDeleteSecret, useTestProvider } from './useProviderHooks'
export { useTrendAnalysis, useDynamicWeights, usePatternAdjustment } from './useAnalysisHooks'
export { useProductStatus, useLocalAppStatus, useRuntimeStatus } from './useSystemHooks'
export { useAlters, useAlterReply } from './useAlterHooks'
export { useCalibrationHistory, useSubmitRealityScore } from './useCalibrationHooks'
export { usePatternReviews, useBuildPatternReview, usePatternReviewDetail } from './usePatternReviewHooks'
export { useBehaviorValidationReport, useEvaluateBehaviorValidation } from './useBehaviorValidationHooks'
export { useDataManifest, useExportData, useDeleteData } from './useDataHooks'
export { useFetchJson, useSuggestRubricDelta, useGenerateCheckpointPlan } from './useMiscHooks'
export { usePredictorProfiles, usePredictorProfile, useCreatePredictorProfile, useOutcomeTargets, useCreateOutcomeTarget, useEvaluateOutcomeTarget, useBranchForecast, useCalibrationDivergence } from './usePredictionHooks'
export { useForecastSnapshots, useForecastSnapshot, useCreateForecastSnapshot, useExternalEvidence, useCreateExternalEvidence, useForecastEvaluations, useCreateForecastEvaluation, useForecastScorecard } from './useForecastHooks'
export { useStartCalibrationConversation, useSendCalibrationMessage, useCalibrationConversation, useCalibrationDrafts, useConfirmCalibrationDraft, useRejectCalibrationDraft } from './useCalibrationConversationHooks'
export { useBehaviorMetricsRecords } from './useBehaviorMetricsHooks'

// Re-export query key factory for convenience
export { queryKeys } from './useQueryKeys'
