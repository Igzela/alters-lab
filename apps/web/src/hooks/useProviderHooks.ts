import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson, deleteJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function useProviderStatus() {
  return useQuery({
    queryKey: queryKeys.providerStatus,
    queryFn: () => fetchJson('/provider-config/status'),
  })
}

export function useProviderConfig() {
  return useQuery({
    queryKey: queryKeys.providerConfig,
    queryFn: () => fetchJson('/provider-config/config'),
  })
}

export function useUpdateProviderConfig() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/provider-config/config', body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.providerConfig })
      qc.invalidateQueries({ queryKey: queryKeys.providerStatus })
    },
  })
}

export function useStoreSecret() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/provider-config/secret', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.providerStatus }),
  })
}

export function useDeleteSecret() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => deleteJson('/provider-config/secret', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.providerStatus }),
  })
}

export function useTestProvider() {
  return useMutation({
    mutationFn: (body: unknown) => postJson('/provider-config/test', body),
  })
}
