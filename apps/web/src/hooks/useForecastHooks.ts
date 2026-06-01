import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

// --- Forecast Snapshots ---

export function useForecastSnapshots() {
  return useQuery({
    queryKey: queryKeys.forecastSnapshots,
    queryFn: () => fetchJson('/forecast-snapshots/list'),
  })
}

export function useForecastSnapshot(id: string | null) {
  return useQuery({
    queryKey: [...queryKeys.forecastSnapshots, id],
    queryFn: () => fetchJson(`/forecast-snapshots/${id}`),
    enabled: !!id,
  })
}

export function useCreateForecastSnapshot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/forecast-snapshots/create-from-forecast', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.forecastSnapshots }),
  })
}

// --- External Evidence ---

export function useExternalEvidence() {
  return useQuery({
    queryKey: queryKeys.externalEvidence,
    queryFn: () => fetchJson('/external-evidence/list'),
  })
}

export function useCreateExternalEvidence() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/external-evidence', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.externalEvidence }),
  })
}

// --- Forecast Evaluations ---

export function useForecastEvaluations() {
  return useQuery({
    queryKey: queryKeys.forecastEvaluations,
    queryFn: () => fetchJson('/forecast-evaluations/list'),
  })
}

export function useCreateForecastEvaluation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/forecast-evaluations/evaluate', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.forecastEvaluations }),
  })
}

// --- Forecast Scorecard ---

export function useForecastScorecard() {
  return useQuery({
    queryKey: queryKeys.forecastScorecard,
    queryFn: () => fetchJson('/forecast-scorecard/summary'),
  })
}
