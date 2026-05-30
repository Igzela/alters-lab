import { useQuery, useMutation } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'

export function useFetchJson<T = unknown>(key: string, path: string, enabled = true) {
  return useQuery<T>({
    queryKey: [key],
    queryFn: () => fetchJson(path),
    enabled,
  })
}

export function useSuggestRubricDelta() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/rubric-delta/suggest', body),
  })
}

export function useGenerateCheckpointPlan() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/checkpoint-regeneration/plan', body),
  })
}
