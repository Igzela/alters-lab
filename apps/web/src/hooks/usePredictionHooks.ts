import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

// --- Predictor Profiles ---

export function usePredictorProfiles() {
  return useQuery({
    queryKey: queryKeys.predictorProfiles,
    queryFn: () => fetchJson('/predictor-profile/list'),
  })
}

export function usePredictorProfile(profileId: string | null) {
  return useQuery({
    queryKey: queryKeys.predictorProfile(profileId),
    queryFn: () => fetchJson(`/predictor-profile/${profileId}`),
    enabled: !!profileId,
  })
}

export function useCreatePredictorProfile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/predictor-profile', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.predictorProfiles }),
  })
}

// --- Branch Outcome Targets ---

export function useOutcomeTargets() {
  return useQuery({
    queryKey: queryKeys.outcomeTargets,
    queryFn: () => fetchJson('/branch-outcome-targets/list'),
  })
}

export function useCreateOutcomeTarget() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/branch-outcome-targets', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.outcomeTargets }),
  })
}

export function useEvaluateOutcomeTarget() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ targetId, body }: { targetId: string; body: unknown }) =>
      postJson(`/branch-outcome-targets/${targetId}/evaluate`, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.outcomeTargets }),
  })
}

// --- Branch Forecast ---

export function useBranchForecast() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/branch-forecast/analyze', body),
  })
}

// --- Calibration Divergence ---

export function useCalibrationDivergence() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/divergence-analysis/analyze', body),
  })
}
