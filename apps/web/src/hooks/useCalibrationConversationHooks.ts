import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJson, postJson } from '../api'
import { queryKeys } from './useQueryKeys'

// --- Start Conversation ---

export function useStartCalibrationConversation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: { branch_id?: string }) =>
      postJson('/calibration-conversation/start', body),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: queryKeys.calibrationConversations }),
  })
}

// --- Send Message ---

export function useSendCalibrationMessage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      conversationId,
      message,
    }: {
      conversationId: string
      message: string
    }) =>
      postJson(`/calibration-conversation/${conversationId}/message`, {
        message,
      }),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({
        queryKey: queryKeys.calibrationConversation(variables.conversationId),
      })
      qc.invalidateQueries({ queryKey: queryKeys.calibrationDrafts })
    },
  })
}

// --- Get Conversation ---

export function useCalibrationConversation(id: string | null) {
  return useQuery({
    queryKey: queryKeys.calibrationConversation(id),
    queryFn: () => fetchJson(`/calibration-conversation/${id}`),
    enabled: !!id,
  })
}

// --- List Drafts ---

export function useCalibrationDrafts() {
  return useQuery({
    queryKey: queryKeys.calibrationDrafts,
    queryFn: () => fetchJson('/calibration-conversation/drafts'),
  })
}

// --- Confirm Draft ---

export function useConfirmCalibrationDraft() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      draftId,
      corrections,
    }: {
      draftId: string
      corrections?: Record<string, unknown>
    }) =>
      postJson(`/calibration-conversation/drafts/${draftId}/confirm`, {
        corrections: corrections ?? {},
      }),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: queryKeys.calibrationDrafts }),
  })
}

// --- Reject Draft ---

export function useRejectCalibrationDraft() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ draftId }: { draftId: string }) =>
      postJson(`/calibration-conversation/drafts/${draftId}/reject`, {}),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: queryKeys.calibrationDrafts }),
  })
}
