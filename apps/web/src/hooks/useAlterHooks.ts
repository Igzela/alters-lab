import { useQuery, useMutation } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function useAlters() {
  return useQuery({
    queryKey: queryKeys.alters,
    queryFn: () => fetchJson('/alter-dialogue/alters'),
  })
}

export function useAlterReply() {
  return useMutation({
    mutationFn: ({ alterId, message }: { alterId: string; message: string }) =>
      postJson(`/provider-dialogue/${alterId}/reply`, { message }),
  })
}
