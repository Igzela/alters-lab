import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function useDataManifest() {
  return useQuery({
    queryKey: queryKeys.dataManifest,
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
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.dataManifest }),
  })
}
