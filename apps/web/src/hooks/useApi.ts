import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchJson,
  postJson,
  deleteJson,
  ingestWeeklyNote,
  editWeeklyNote,
  listWeeklyNotes,
  startWeeklyReview,
  completeWeeklyReview,
  listWeeklyReviews,
  scoreActionAlignment,
  listActionAlignmentScores,
  fetchWeeklyReviewAssistantStatus,
  suggestWeeklyReviewAssistant,
  analyzeTrend,
  computeDynamicWeights,
  adjustForecast,
} from '../api'
import type { WeeklyNoteRecord, WeeklyReviewSession } from '../types'

// --- Generic fetch hook for endpoints without dedicated wrappers ---
export function useFetchJson<T = unknown>(key: string, path: string, enabled = true) {
  return useQuery<T>({
    queryKey: [key],
    queryFn: () => fetchJson(path),
    enabled,
  })
}

// --- Weekly Notes ---
export function useWeeklyNotes() {
  return useQuery({
    queryKey: ['weekly-notes'],
    queryFn: listWeeklyNotes,
  })
}

export function useIngestWeeklyNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ingestWeeklyNote,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekly-notes'] }),
  })
}

export function useEditWeeklyNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ recordId, body }: { recordId: string; body: Partial<WeeklyNoteRecord> & { correction_note: string } }) =>
      editWeeklyNote(recordId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekly-notes'] }),
  })
}

// --- Weekly Reviews ---
export function useWeeklyReviews() {
  return useQuery({
    queryKey: ['weekly-reviews'],
    queryFn: listWeeklyReviews,
  })
}

export function useStartWeeklyReview() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ noteId, alterId }: { noteId: string; alterId: string | null }) =>
      startWeeklyReview(noteId, alterId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekly-reviews'] }),
  })
}

export function useCompleteWeeklyReview() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ sessionId, body }: {
      sessionId: string
      body: { review_note: string; dialogue_summary: string; primary_next_correction: string; supporting_actions: string[] }
    }) => completeWeeklyReview(sessionId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekly-reviews'] }),
  })
}

// --- Action Alignment ---
export function useActionAlignmentScores() {
  return useQuery({
    queryKey: ['action-alignment-scores'],
    queryFn: listActionAlignmentScores,
  })
}

export function useScoreActionAlignment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: scoreActionAlignment,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['action-alignment-scores'] }),
  })
}

// --- Weekly Review Assistant ---
export function useWeeklyReviewAssistantStatus() {
  return useQuery({
    queryKey: ['weekly-review-assistant-status'],
    queryFn: fetchWeeklyReviewAssistantStatus,
  })
}

export function useSuggestWeeklyReviewAssistant() {
  return useMutation({
    mutationFn: suggestWeeklyReviewAssistant,
  })
}

// --- Provider Config ---
export function useProviderStatus() {
  return useQuery({
    queryKey: ['provider-status'],
    queryFn: () => fetchJson('/provider-config/status'),
  })
}

export function useProviderConfig() {
  return useQuery({
    queryKey: ['provider-config'],
    queryFn: () => fetchJson('/provider-config/config'),
  })
}

export function useUpdateProviderConfig() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/provider-config/config', body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['provider-config'] })
      qc.invalidateQueries({ queryKey: ['provider-status'] })
    },
  })
}

export function useStoreSecret() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/provider-config/secret', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['provider-status'] }),
  })
}

export function useDeleteSecret() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => deleteJson('/provider-config/secret', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['provider-status'] }),
  })
}

export function useTestProvider() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/provider-config/test', body),
  })
}

// --- System Status ---
export function useProductStatus() {
  return useQuery({
    queryKey: ['product-status'],
    queryFn: () => fetchJson('/product/status'),
  })
}

export function useLocalAppStatus() {
  return useQuery({
    queryKey: ['local-app-status'],
    queryFn: () => fetchJson('/local-app/status'),
  })
}

export function useRuntimeStatus() {
  return useQuery({
    queryKey: ['runtime-status'],
    queryFn: () => fetchJson('/runtime-layout/status'),
  })
}

// --- Alter Dialogue ---
export function useAlters() {
  return useQuery({
    queryKey: ['alters'],
    queryFn: () => fetchJson('/alter-dialogue/alters'),
  })
}

export function useAlterReply() {
  return useMutation({
    mutationFn: ({ alterId, message }: { alterId: string; message: string }) =>
      postJson(`/provider-dialogue/${alterId}/reply`, { message }),
  })
}

// --- Calibration / Reality Score ---
export function useCalibrationHistory() {
  return useQuery({
    queryKey: ['calibration-history'],
    queryFn: () => fetchJson('/calibration-loop/history'),
  })
}

export function useSubmitRealityScore() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/calibration-loop/reality-scores', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['calibration-history'] }),
  })
}

// --- Rubric Delta ---
export function useSuggestRubricDelta() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/rubric-delta/suggest', body),
  })
}

// --- Checkpoint Plan ---
export function useGenerateCheckpointPlan() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/checkpoint-regeneration/plan', body),
  })
}

// --- Pattern Review ---
export function usePatternReviews() {
  return useQuery({
    queryKey: ['pattern-reviews'],
    queryFn: () => fetchJson('/pattern-review/list'),
  })
}

export function useBuildPatternReview() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/pattern-review/build', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pattern-reviews'] }),
  })
}

export function usePatternReviewDetail(reviewId: string | null) {
  return useQuery({
    queryKey: ['pattern-review', reviewId],
    queryFn: () => fetchJson(`/pattern-review/${reviewId}`),
    enabled: !!reviewId,
  })
}

// --- Behavior Validation ---
export function useBehaviorValidationReport() {
  return useQuery({
    queryKey: ['behavior-validation'],
    queryFn: () => fetchJson('/behavior-validation/report'),
  })
}

export function useEvaluateBehaviorValidation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/behavior-validation/evaluate', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['behavior-validation'] }),
  })
}

// --- Data Management ---
export function useDataManifest() {
  return useQuery({
    queryKey: ['data-manifest'],
    queryFn: () => fetchJson('/p6-data-retention/manifest'),
  })
}

export function useExportData() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/p6-data-retention/export', body),
  })
}

export function useDeleteData() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/p6-data-retention/delete', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['data-manifest'] }),
  })
}

// --- Trend Analysis ---
export function useTrendAnalysis(lookbackWeeks = 8, forecastWeeks = 4) {
  return useQuery({
    queryKey: ['trend-analysis', lookbackWeeks, forecastWeeks],
    queryFn: () => analyzeTrend({ lookback_weeks: lookbackWeeks, forecast_weeks: forecastWeeks }),
  })
}

// --- Dynamic Weights ---
export function useDynamicWeights(lookbackWeeks = 8) {
  return useQuery({
    queryKey: ['dynamic-weights', lookbackWeeks],
    queryFn: () => computeDynamicWeights({ lookback_weeks: lookbackWeeks }),
  })
}

// --- Pattern Adjustment ---
export function usePatternAdjustment(lookbackWeeks = 8, forecastWeeks = 4) {
  return useQuery({
    queryKey: ['pattern-adjustment', lookbackWeeks, forecastWeeks],
    queryFn: () => adjustForecast({ lookback_weeks: lookbackWeeks, forecast_weeks: forecastWeeks }),
  })
}
