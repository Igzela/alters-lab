import { useQuery } from '@tanstack/react-query'
import { fetchJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function useBehaviorMetricsRecords() {
  return useQuery({
    queryKey: queryKeys.behaviorMetricsRecords,
    queryFn: () =>
      fetchJson('/behavior-metrics/weekly-records') as Promise<{
        status: string
        records: Array<Record<string, unknown>>
        count: number
      }>,
  })
}
