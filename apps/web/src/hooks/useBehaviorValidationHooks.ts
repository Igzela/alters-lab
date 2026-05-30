import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function useBehaviorValidationReport() {
  return useQuery({
    queryKey: queryKeys.behaviorValidation,
    queryFn: () => fetchJson('/behavior-validation/report'),
  })
}

export function useEvaluateBehaviorValidation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/behavior-validation/evaluate', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.behaviorValidation }),
  })
}
