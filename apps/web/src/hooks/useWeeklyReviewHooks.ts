import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listWeeklyReviews, startWeeklyReview, completeWeeklyReview, fetchWeeklyReviewAssistantStatus, suggestWeeklyReviewAssistant } from '../api'
import { queryKeys } from './useQueryKeys'

export function useWeeklyReviews() {
  return useQuery({
    queryKey: queryKeys.weeklyReviews,
    queryFn: listWeeklyReviews,
  })
}

export function useStartWeeklyReview() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ noteId, alterId }: { noteId: string; alterId: string | null }) =>
      startWeeklyReview(noteId, alterId),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.weeklyReviews }),
  })
}

export function useCompleteWeeklyReview() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ sessionId, body }: {
      sessionId: string
      body: { review_note: string; dialogue_summary: string; primary_next_correction: string; supporting_actions: string[] }
    }) => completeWeeklyReview(sessionId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.weeklyReviews }),
  })
}

export function useWeeklyReviewAssistantStatus() {
  return useQuery({
    queryKey: queryKeys.weeklyReviewAssistantStatus,
    queryFn: fetchWeeklyReviewAssistantStatus,
  })
}

export function useSuggestWeeklyReviewAssistant() {
  return useMutation({
    mutationFn: suggestWeeklyReviewAssistant,
  })
}
