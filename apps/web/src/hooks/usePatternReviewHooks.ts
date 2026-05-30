import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function usePatternReviews() {
  return useQuery({
    queryKey: queryKeys.patternReviews,
    queryFn: () => fetchJson('/pattern-review/list'),
  })
}

export function useBuildPatternReview() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: unknown) => postJson('/pattern-review/build', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.patternReviews }),
  })
}

export function usePatternReviewDetail(reviewId: string | null) {
  return useQuery({
    queryKey: queryKeys.patternReviewDetail(reviewId),
    queryFn: () => fetchJson(`/pattern-review/${reviewId}`),
    enabled: !!reviewId,
  })
}
