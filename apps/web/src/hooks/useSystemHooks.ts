import { useQuery } from '@tanstack/react-query'
import { fetchJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function useProductStatus() {
  return useQuery({
    queryKey: queryKeys.productStatus,
    queryFn: () => fetchJson('/product/status'),
  })
}

export function useLocalAppStatus() {
  return useQuery({
    queryKey: queryKeys.localAppStatus,
    queryFn: () => fetchJson('/local-app/status'),
  })
}

export function useRuntimeStatus() {
  return useQuery({
    queryKey: queryKeys.runtimeStatus,
    queryFn: () => fetchJson('/runtime-layout/status'),
  })
}
