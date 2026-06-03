import { useQuery } from '@tanstack/react-query'
import { fetchJson } from '../api'
import { queryKeys } from './useQueryKeys'

export function usePublicPriorArtifacts(approvedOnly = true) {
  return useQuery({
    queryKey: [...queryKeys.publicPriorArtifacts, approvedOnly],
    queryFn: () => fetchJson(`/public-priors/artifacts?approved_only=${approvedOnly}`),
  })
}

export function usePublicPriorArtifact(artifactId: string | null) {
  return useQuery({
    queryKey: [...queryKeys.publicPriorArtifacts, artifactId],
    queryFn: () => fetchJson(`/public-priors/artifacts/${artifactId}`),
    enabled: !!artifactId,
  })
}

export function usePublicPriorModelCards() {
  return useQuery({
    queryKey: queryKeys.publicPriorModelCards,
    queryFn: () => fetchJson('/public-priors/model-cards'),
  })
}

export function usePublicPriorModelCard(modelId: string | null) {
  return useQuery({
    queryKey: [...queryKeys.publicPriorModelCards, modelId],
    queryFn: () => fetchJson(`/public-priors/model-cards/${modelId}`),
    enabled: !!modelId,
  })
}

export function usePublicPriorCoverage() {
  return useQuery({
    queryKey: queryKeys.publicPriorCoverage,
    queryFn: () => fetchJson('/public-priors/coverage'),
  })
}
