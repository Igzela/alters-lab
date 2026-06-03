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
    contextual_prior_count: number
    best_confidence: string
    best_transfer_risk: string
    prior_direction: string
    model_family: string
    artifact_class: string
    artifact_ids: string[]
    route_b_status: string
  }> | undefined

  if (!data) return null

  const domains = Object.keys(data)

  const approvedCount = domains.filter(d => data[d].has_approved_artifact).length
  const totalArtifacts = domains.reduce((sum, d) => sum + data[d].artifact_count, 0)
  const lowRiskCount = domains.filter(d => data[d].best_transfer_risk === 'low').length

  return (
    <div className="space-y-4">
      {/* Baseline Summary */}
      <Card>
        <div className="p-4">
          <h3 className="font-semibold mb-3">{t('publicPriors.coverage.baselineSummary')}</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color: 'var(--color-accent)' }}>{approvedCount}/5</div>
              <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{t('publicPriors.coverage.domainsApproved')}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color: 'var(--color-accent)' }}>{totalArtifacts}</div>
              <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{t('publicPriors.coverage.totalArtifacts')}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color: 'var(--color-accent)' }}>{lowRiskCount}</div>
              <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{t('publicPriors.coverage.lowRiskDomains')}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color: 'var(--color-accent)' }}>2</div>
              <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{t('publicPriors.coverage.sourceDatasets')}</div>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="font-semibold mb-3">{t('publicPriors.coverage.domainMatrix')}</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <th className="text-left py-2 px-2 font-medium">{t('publicPriors.coverage.domain')}</th>
                  <th className="text-center py-2 px-2 font-medium">Route B Status</th>
                  <th className="text-center py-2 px-2 font-medium">Class</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.direction')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.confidence')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('publicPriors.coverage.transferRisk')}</th>
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
                        <Badge variant={d.route_b_status === 'approved' ? 'success' : d.route_b_status === 'contextual_only' ? 'warning' : 'muted'}>
                          {d.route_b_status === 'approved' ? 'Route B Approved' : d.route_b_status === 'contextual_only' ? 'Contextual Only' : 'No Prior'}
                        </Badge>
                      </td>
                      <td className="py-2 px-2 text-center text-xs">{d.artifact_class === 'data_backed_baseline' ? 'Data-Backed' : d.artifact_class === 'calibrated_model' ? 'Calibrated Model' : d.artifact_class === 'contextual_prior' ? 'Contextual' : d.artifact_class}</td>
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
                      <td className="py-2 px-2 text-center">{d.artifact_count}{d.contextual_prior_count > 0 ? ` +${d.contextual_prior_count}c` : ''}</td>
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
              const variant = d.route_b_status === 'approved' ? 'success' : d.route_b_status === 'contextual_only' ? 'warning' : 'error'
              const label = d.route_b_status === 'approved' ? 'Route B Approved' : d.route_b_status === 'contextual_only' ? 'Contextual Only' : 'No Prior'
              return (
                <Badge key={domain} variant={variant}>
                  {DOMAIN_LABELS[domain] || domain}: {label}
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
    probability_band?: string | null
    population_percentile?: number | null
    deviation_from_baseline?: number | null
    artifact_class?: string
    actual_data_used?: boolean
    baseline_table_id?: string | null
    value_labels_confirmed?: boolean
    missingness_reviewed?: boolean
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
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="info">Direction: {artifact.prior_direction}</Badge>
              {artifact.artifact_class === 'data_backed_baseline' && (
                <Badge variant="success">Data-Backed</Badge>
              )}
              {artifact.artifact_class === 'calibrated_model' && (
                <Badge variant="success">Calibrated Model</Badge>
              )}
              {artifact.artifact_class === 'contextual_prior' && (
                <Badge variant="warning">Contextual Only</Badge>
              )}
              {artifact.actual_data_used && (
                <Badge variant="success">Actual Data</Badge>
              )}
              {artifact.value_labels_confirmed && (
                <Badge variant="info">Value Labels Confirmed</Badge>
              )}
              {artifact.missingness_reviewed && (
                <Badge variant="info">Missingness Reviewed</Badge>
              )}
              {artifact.baseline_table_id && (
                <Badge variant="muted">Table: {artifact.baseline_table_id}</Badge>
              )}
              {artifact.population_percentile != null && (
                <Badge variant="info">Percentile: {artifact.population_percentile}</Badge>
              )}
              {artifact.probability_band && (
                <Badge variant="info">Band: {artifact.probability_band}</Badge>
              )}
            </div>
            {/* Missingness / Transfer Risk Detail */}
            <div className="mt-2 p-2 rounded text-xs" style={{ backgroundColor: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
              <div className="font-medium mb-1">{t('publicPriors.artifacts.transferRiskDetail')}</div>
              <div className="flex gap-4">
                <span>Transfer Risk: <Badge variant={RISK_COLORS[artifact.transfer_risk] || 'muted'}>{artifact.transfer_risk}</Badge></span>
                <span>Confidence: <Badge variant={CONFIDENCE_COLORS[artifact.confidence] || 'muted'}>{artifact.confidence}</Badge></span>
                <span>Type: {artifact.prior_type}</span>
              </div>
              {artifact.transfer_risk === 'high' && (
                <p className="mt-1" style={{ color: 'var(--color-error)' }}>
                  {t('publicPriors.artifacts.highRiskWarning')}
                </p>
              )}
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
    feature_mapping_ids: string[]
    model_family: string
    training_status: string
    evaluation_summary: string
    transfer_risk: string
    approved_for_route_b: boolean
    limitations: string[]
    artifact_class?: string
    approval_level?: string
    approval_reason?: string
    approval_blockers?: string[]
    calibration_metrics?: {
      brier_score?: number | null
      calibration_slope?: number | null
      auc?: number | null
      r2?: number | null
    }
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
            {card.approval_level === 'route_b_approved' && (
              <Badge variant="success" className="ml-1.5">Route B</Badge>
            )}
            {card.approval_level === 'lab_only' && (
              <Badge variant="warning" className="ml-1.5">Lab Only</Badge>
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
                <Badge variant={selected.approval_level === 'route_b_approved' ? 'success' : selected.approval_level === 'lab_only' ? 'warning' : 'muted'}>
                  {selected.approval_level === 'route_b_approved' ? 'Route B Approved' : selected.approval_level === 'lab_only' ? 'Lab Only' : 'Unapproved'}
                </Badge>
                {selected.artifact_class && (
                  <Badge variant={selected.artifact_class === 'data_backed_baseline' || selected.artifact_class === 'calibrated_model' ? 'success' : selected.artifact_class === 'contextual_prior' ? 'warning' : 'info'}>
                    {selected.artifact_class === 'data_backed_baseline' ? 'Data-Backed' : selected.artifact_class === 'calibrated_model' ? 'Calibrated Model' : selected.artifact_class === 'contextual_prior' ? 'Contextual' : selected.artifact_class}
                  </Badge>
                )}
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
            {/* Value Labels / Feature Mappings */}
            {selected.feature_mapping_ids?.length > 0 && (
              <div className="mt-2">
                <h5 className="text-xs font-medium mb-1">{t('publicPriors.modelCards.featureMappings')}</h5>
                <div className="flex flex-wrap gap-1">
                  {selected.feature_mapping_ids.map(fid => (
                    <Badge key={fid} variant="muted">{fid}</Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Calibration Metrics */}
            {selected.calibration_metrics && Object.values(selected.calibration_metrics).some(v => v != null) && (
              <div className="mt-2 p-3 rounded" style={{
                backgroundColor: selected.artifact_class === 'calibrated_model' ? 'var(--color-accent-bg)' : 'var(--color-bg-secondary)',
                border: selected.artifact_class === 'calibrated_model' ? '1px solid var(--color-accent)' : '1px solid var(--color-border)',
              }}>
                <div className="font-medium mb-1 flex items-center gap-2">
                  {t('publicPriors.modelCards.calibrationMetrics')}
                  {selected.artifact_class === 'calibrated_model' && (
                    <Badge variant="success">Primary Validation</Badge>
                  )}
                </div>
                <div className="flex gap-4 flex-wrap text-xs">
                  {selected.calibration_metrics.brier_score != null && (
                    <span className="font-mono">Brier: {selected.calibration_metrics.brier_score.toFixed(3)}</span>
                  )}
                  {selected.calibration_metrics.calibration_slope != null && (
                    <span className="font-mono">Slope: {selected.calibration_metrics.calibration_slope.toFixed(3)}</span>
                  )}
                  {selected.calibration_metrics.auc != null && (
                    <span className="font-mono">AUC: {selected.calibration_metrics.auc.toFixed(3)}</span>
                  )}
                  {selected.calibration_metrics.r2 != null && (
                    <span className="font-mono">R²: {selected.calibration_metrics.r2.toFixed(3)}</span>
                  )}
                </div>
              </div>
            )}

            {/* Approval & Transfer Risk */}
            <div className="mt-2 p-2 rounded text-xs" style={{ backgroundColor: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
              <div className="font-medium mb-1">Approval Status</div>
              <div className="flex gap-4 flex-wrap">
                <span>Level: <Badge variant={selected.approval_level === 'route_b_approved' ? 'success' : selected.approval_level === 'lab_only' ? 'warning' : 'muted'}>{selected.approval_level || 'unapproved'}</Badge></span>
                <span>Class: {selected.artifact_class || 'unknown'}</span>
                <span>Transfer Risk: <Badge variant={RISK_COLORS[selected.transfer_risk] || 'muted'}>{selected.transfer_risk}</Badge></span>
              </div>
              {selected.approval_reason && (
                <p className="mt-1">{selected.approval_reason}</p>
              )}
              {selected.approval_blockers && selected.approval_blockers.length > 0 && (
                <div className="mt-1">
                  <span style={{ color: 'var(--color-error)' }}>Blockers: </span>
                  {selected.approval_blockers.join(', ')}
                </div>
              )}
              {selected.transfer_risk === 'high' && (
                <p className="mt-1" style={{ color: 'var(--color-error)' }}>
                  {t('publicPriors.modelCards.highRiskWarning')}
                </p>
              )}
            </div>

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
