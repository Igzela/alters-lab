import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  usePublicPriorArtifacts,
  usePublicPriorModelCards,
  usePublicPriorCoverage,
} from '../hooks/usePublicPriorHooks'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import ErrorDisplay from '../components/ErrorDisplay'

function ErrorMessage({ error }: { error: unknown }) {
  const message = error instanceof Error ? error.message : String(error)
  return <ErrorDisplay message={message} />
}
import { Skeleton } from '../components/Skeleton'

type Tab = 'coverage' | 'artifacts' | 'model-cards'

const RISK_COLORS: Record<string, 'success' | 'warning' | 'error' | 'muted'> = {
  low: 'success',
  medium: 'warning',
  high: 'error',
}

const CONFIDENCE_COLORS: Record<string, 'success' | 'warning' | 'error' | 'muted'> = {
  high: 'success',
  medium: 'warning',
  low: 'error',
}

const DOMAIN_LABELS: Record<string, string> = {
  career_education: 'Career & Education',
  financial: 'Financial',
  health: 'Health',
  relationship: 'Relationship',
  subjective_wellbeing: 'Subjective Wellbeing',
}

export default function PublicPriors() {
  const { t } = useTranslation()
  const [tab, setTab] = useState<Tab>('coverage')
  const [selectedCard, setSelectedCard] = useState<string | null>(null)

  const coverage = usePublicPriorCoverage()
  const artifacts = usePublicPriorArtifacts()
  const modelCards = usePublicPriorModelCards()

  const tabs: { key: Tab; label: string }[] = [
    { key: 'coverage', label: t('publicPriors.tabs.coverage') },
    { key: 'artifacts', label: t('publicPriors.tabs.artifacts') },
    { key: 'model-cards', label: t('publicPriors.tabs.modelCards') },
  ]

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('publicPriors.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
        {t('publicPriors.description')}
      </p>

      <div className="flex gap-1 border-b" style={{ borderColor: 'var(--color-border)' }}>
        {tabs.map(tb => (
          <button
            key={tb.key}
            onClick={() => setTab(tb.key)}
            className="px-3 py-1.5 text-sm font-medium transition-colors border-b-2 -mb-px"
            style={{
              borderColor: tab === tb.key ? 'var(--color-accent)' : 'transparent',
              color: tab === tb.key ? 'var(--color-text)' : 'var(--color-text-secondary)',
            }}
          >
            {tb.label}
          </button>
        ))}
      </div>

      {tab === 'coverage' && <CoverageTab coverage={coverage} />}
      {tab === 'artifacts' && <ArtifactsTab artifacts={artifacts} />}
      {tab === 'model-cards' && (
        <ModelCardsTab
          modelCards={modelCards}
          selectedCard={selectedCard}
          onSelectCard={setSelectedCard}
        />
      )}
    </div>
  )
}

function CoverageTab({ coverage }: { coverage: ReturnType<typeof usePublicPriorCoverage> }) {
  const { t } = useTranslation()

  if (coverage.isLoading) return <Skeleton className="h-48" />
  if (coverage.error) return <ErrorMessage error={coverage.error} />

  const data = coverage.data as Record<string, {
    has_approved_artifact: boolean
    artifact_count: number
    best_confidence: string
    best_transfer_risk: string
    prior_direction: string
    model_family: string
    artifact_ids: string[]
  }> | undefined

  if (!data) return null

  const domains = Object.keys(data)

  return (
    <div className="space-y-4">
      <Card>
        <div className="p-4">
          <h3 className="font-semibold mb-3">{t('publicPriors.coverage.domainMatrix')}</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <th className="text-left py-2 px-2 font-medium">{t('publicPriors.coverage.domain')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.status')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.direction')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.confidence')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.transferRisk')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.modelFamily')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.artifacts')}</th>
                </tr>
              </thead>
              <tbody>
                {domains.map(domain => {
                  const d = data[domain]
                  return (
                    <tr key={domain} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td className="py-2 px-2 font-medium">{DOMAIN_LABELS[domain] || domain}</td>
                      <td className="py-2 px-2 text-center">
                        <Badge variant={d.has_approved_artifact ? 'success' : 'muted'}>
                          {d.has_approved_artifact ? 'Approved' : 'None'}
                        </Badge>
                      </td>
                      <td className="py-2 px-2 text-center capitalize">{d.prior_direction}</td>
                      <td className="py-2 px-2 text-center">
                        <Badge variant={CONFIDENCE_COLORS[d.best_confidence] || 'muted'}>
                          {d.best_confidence}
                        </Badge>
                      </td>
                      <td className="py-2 px-2 text-center">
                        <Badge variant={RISK_COLORS[d.best_transfer_risk] || 'muted'}>
                          {d.best_transfer_risk}
                        </Badge>
                      </td>
                      <td className="py-2 px-2 text-center text-xs">{d.model_family}</td>
                      <td className="py-2 px-2 text-center">{d.artifact_count}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="font-semibold mb-2">{t('publicPriors.coverage.routeBSummary')}</h3>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {t('publicPriors.coverage.routeBExplanation')}
          </p>
          <div className="mt-3 flex gap-2 flex-wrap">
            {domains.map(domain => {
              const d = data[domain]
              return (
                <Badge key={domain} variant={d.has_approved_artifact ? 'success' : 'error'}>
                  {DOMAIN_LABELS[domain] || domain}: {d.has_approved_artifact ? 'Route B Available' : 'Route A Only'}
                </Badge>
              )
            })}
          </div>
        </div>
      </Card>
    </div>
  )
}

function ArtifactsTab({ artifacts }: { artifacts: ReturnType<typeof usePublicPriorArtifacts> }) {
  const { t } = useTranslation()

  if (artifacts.isLoading) return <Skeleton className="h-48" />
  if (artifacts.error) return <ErrorMessage error={artifacts.error} />

  const data = artifacts.data as { artifacts: Array<{
    artifact_id: string
    model_id: string
    domain: string
    prior_type: string
    prior_direction: string
    confidence: string
    transfer_risk: string
    explanation: string
    limitations: string[]
  }> } | undefined

  if (!data?.artifacts?.length) {
    return (
      <Card>
        <div className="p-4 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          {t('publicPriors.artifacts.empty')}
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {data.artifacts.map(artifact => (
        <Card key={artifact.artifact_id}>
          <div className="p-4">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h4 className="font-semibold">{artifact.artifact_id}</h4>
                <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>
                  {DOMAIN_LABELS[artifact.domain] || artifact.domain} · {artifact.prior_type} · Model: {artifact.model_id}
                </p>
              </div>
              <div className="flex gap-1.5">
                <Badge variant={CONFIDENCE_COLORS[artifact.confidence] || 'muted'}>
                  {artifact.confidence}
                </Badge>
                <Badge variant={RISK_COLORS[artifact.transfer_risk] || 'muted'}>
                  {artifact.transfer_risk} risk
                </Badge>
              </div>
            </div>
            <p className="text-sm mb-2" style={{ color: 'var(--color-text-secondary)' }}>
              {artifact.explanation}
            </p>
            <div className="flex items-center gap-2">
              <Badge variant="info">Direction: {artifact.prior_direction}</Badge>
            </div>
            {artifact.limitations?.length > 0 && (
              <details className="mt-2">
                <summary className="text-xs cursor-pointer" style={{ color: 'var(--color-text-secondary)' }}>
                  {t('publicPriors.artifacts.limitations')} ({artifact.limitations.length})
                </summary>
                <ul className="mt-1 text-xs space-y-0.5" style={{ color: 'var(--color-text-secondary)' }}>
                  {artifact.limitations.map((lim, i) => (
                    <li key={i}>· {lim}</li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        </Card>
      ))}
    </div>
  )
}

function ModelCardsTab({
  modelCards,
  selectedCard,
  onSelectCard,
}: {
  modelCards: ReturnType<typeof usePublicPriorModelCards>
  selectedCard: string | null
  onSelectCard: (id: string | null) => void
}) {
  const { t } = useTranslation()

  if (modelCards.isLoading) return <Skeleton className="h-48" />
  if (modelCards.error) return <ErrorMessage error={modelCards.error} />

  const data = modelCards.data as { model_cards: Array<{
    model_id: string
    source_dataset_ids: string[]
    outcome_id: string
    model_family: string
    training_status: string
    evaluation_summary: string
    transfer_risk: string
    approved_for_route_b: boolean
    limitations: string[]
  }> } | undefined

  if (!data?.model_cards?.length) {
    return (
      <Card>
        <div className="p-4 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          {t('publicPriors.modelCards.empty')}
        </div>
      </Card>
    )
  }

  const selected = selectedCard ? data.model_cards.find(c => c.model_id === selectedCard) : null

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {data.model_cards.map(card => (
          <button
            key={card.model_id}
            onClick={() => onSelectCard(selectedCard === card.model_id ? null : card.model_id)}
            className="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            style={{
              borderColor: selectedCard === card.model_id ? 'var(--color-accent)' : 'var(--color-border)',
              backgroundColor: selectedCard === card.model_id ? 'var(--color-accent-bg)' : 'transparent',
              color: 'var(--color-text)',
            }}
          >
            {card.model_id}
            {card.approved_for_route_b && (
              <Badge variant="success" className="ml-1.5">Approved</Badge>
            )}
          </button>
        ))}
      </div>

      {selected && (
        <Card>
          <div className="p-4">
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-semibold">{selected.model_id}</h4>
              <div className="flex gap-1.5">
                <Badge variant={selected.approved_for_route_b ? 'success' : 'muted'}>
                  {selected.approved_for_route_b ? 'Approved for Route B' : 'Not Approved'}
                </Badge>
                <Badge variant={RISK_COLORS[selected.transfer_risk] || 'muted'}>
                  {selected.transfer_risk} risk
                </Badge>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm mb-3">
              <div>
                <span className="font-medium">{t('publicPriors.modelCards.family')}:</span> {selected.model_family}
              </div>
              <div>
                <span className="font-medium">{t('publicPriors.modelCards.status')}:</span> {selected.training_status}
              </div>
              <div>
                <span className="font-medium">{t('publicPriors.modelCards.outcome')}:</span> {selected.outcome_id}
              </div>
              <div>
                <span className="font-medium">{t('publicPriors.modelCards.datasets')}:</span> {selected.source_dataset_ids.join(', ')}
              </div>
            </div>
            {selected.evaluation_summary && (
              <p className="text-sm mb-2" style={{ color: 'var(--color-text-secondary)' }}>
                {selected.evaluation_summary}
              </p>
            )}
            {selected.limitations?.length > 0 && (
              <details className="mt-2" open>
                <summary className="text-xs font-medium cursor-pointer" style={{ color: 'var(--color-text-secondary)' }}>
                  {t('publicPriors.modelCards.limitations')} ({selected.limitations.length})
                </summary>
                <ul className="mt-1 text-xs space-y-0.5" style={{ color: 'var(--color-text-secondary)' }}>
                  {selected.limitations.map((lim, i) => (
                    <li key={i}>· {lim}</li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}
