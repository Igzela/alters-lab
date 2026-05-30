import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ingestWeeklyNote, editWeeklyNote, listWeeklyNotes } from '../api'
import type { WeeklyNoteRecord } from '../types'
import { queryKeys } from './useQueryKeys'

export function useWeeklyNotes() {
  return useQuery({
    queryKey: queryKeys.weeklyNotes,
    queryFn: listWeeklyNotes,
  })
}

export function useIngestWeeklyNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ingestWeeklyNote,
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.weeklyNotes }),
  })
}

export function useEditWeeklyNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ recordId, body }: { recordId: string; body: Partial<WeeklyNoteRecord> & { correction_note: string } }) =>
      editWeeklyNote(recordId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.weeklyNotes }),
  })
}
