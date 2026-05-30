import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function useCalibrationHistory() {
  return useQuery({
    queryKey: queryKeys.calibrationHistory,
    queryFn: () => fetchJson('/calibration-loop/history'),
  })
}

export function useSubmitRealityScore() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/calibration-loop/reality-scores', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.calibrationHistory }),
  })
}
