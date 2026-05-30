import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listActionAlignmentScores, scoreActionAlignment } from '../api'
import { queryKeys } from './useQueryKeys'

export function useActionAlignmentScores() {
  return useQuery({
    queryKey: queryKeys.actionAlignmentScores,
    queryFn: listActionAlignmentScores,
  })
}

export function useScoreActionAlignment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: scoreActionAlignment,
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.actionAlignmentScores }),
  })
}
