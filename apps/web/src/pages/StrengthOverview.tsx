import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { usePublicPriorCoverage, usePublicPriorModelCards } from '../hooks/usePublicPriorHooks'
import { usePredictorProfiles } from '../hooks/usePredictionHooks'
import { useCalibrationHistory } from '../hooks/useApi'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Skeleton } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'

const DOMAIN_LABELS: Record<string, string> = {
  career_education: 'Career & Education',
  financial: 'Financial',
  health: 'Health',
  relationship: 'Relationship',
  subjective_wellbeing: 'Subjective Wellbeing',
}

const STRENGTH_ORDER = ['strong_calibrated', 'data_backed', 'contextual', 'none'] as const
type StrengthLevel = (typeof STRENGTH_ORDER)[number]

const STRENGTH_BADGE: Record<StrengthLevel, 'success' | 'warning' | 'info' | 'muted'> = {
  strong_calibrated: 'success',
  data_backed: 'warning',
  contextual: 'info',
  none: 'muted',
}

interface DomainCoverage {
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
  strength_level: string
}

function strengthIndex(level: string): number {
  const idx = STRENGTH_ORDER.indexOf(level as StrengthLevel)
  return idx >= 0 ? idx : STRENGTH_ORDER.length
}

export default function StrengthOverview() {
  const { t } = useTranslation()
  const coverage = usePublicPriorCoverage()
  const modelCards = usePublicPriorModelCards()
  const profiles = usePredictorProfiles()
  const calibration = useCalibrationHistory()

  const isLoading = coverage.isLoading || modelCards.isLoading
  const error = coverage.error || modelCards.error

  const coverageData = coverage.data as Record<string, DomainCoverage> | undefined
  const cardsData = modelCards.data as { model_cards: Array<Record<string, unknown>> } | undefined
  const profilesData = profiles.data as { profiles: Array<Record<string, unknown>> } | undefined
  const calibrationData = calibration.data as { records: Array<Record<string, unknown>>; count: number } | undefined

  const sortedDomains = useMemo(() => {
    if (!coverageData) return []
    return Object.keys(coverageData).sort(
      (a, b) => strengthIndex(coverageData[a].strength_level) - strengthIndex(coverageData[b].strength_level)
    )
  }, [coverageData])

  const stats = useMemo((): StrengthStats | null => {
    if (!coverageData) return null
    const domains = Object.values(coverageData)
    return {
      strongCount: domains.filter(d => d.strength_level === 'strong_calibrated').length,
      dataBackedCount: domains.filter(d => d.strength_level === 'data_backed').length,
      contextualCount: domains.filter(d => d.strength_level === 'contextual').length,
      noneCount: domains.filter(d => d.strength_level === 'none').length,
      approvedCount: domains.filter(d => d.has_approved_artifact).length,
      totalModels: cardsData?.model_cards?.length ?? 0,
      totalProfiles: profilesData?.profiles?.length ?? 0,
      calibrationRecords: calibrationData?.count ?? 0,
    }
  }, [coverageData, cardsData, profilesData, calibrationData])

  if (isLoading) return <Skeleton className="h-48" />
  if (error) return <ErrorDisplay message={error instanceof Error ? error.message : String(error)} />

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold tracking-tight">{t('strengthOverview.title')}</h2>
        <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          {t('strengthOverview.description')}
        </p>
      </div>

      {stats && <SummaryStats stats={stats} />}

      <Card>
        <div className="p-4">
          <h3 className="font-semibold mb-3">{t('strengthOverview.domainMatrix')}</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <th className="text-left py-2 px-2 font-medium">{t('strengthOverview.domain')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('strengthOverview.strengthLevel')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('strengthOverview.routeBStatus')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('strengthOverview.modelFamily')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('strengthOverview.confidence')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('strengthOverview.transferRisk')}</th>
                  <th className="text-center py-2 px-2 font-medium">{t('strengthOverview.artifacts')}</th>
                </tr>
              </thead>
              <tbody>
                {sortedDomains.map(domain => {
                  const d = coverageData![domain]
                  const level = d.strength_level as StrengthLevel
                  return (
                    <tr key={domain} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td className="py-2 px-2 font-medium">{DOMAIN_LABELS[domain] || domain}</td>
                      <td className="py-2 px-2 text-center">
                        <Badge variant={STRENGTH_BADGE[level] || 'muted'}>
                          {t(`strengthOverview.levels.${level}`)}
                        </Badge>
                      </td>
                      <td className="py-2 px-2 text-center">
                        <Badge variant={d.route_b_status === 'approved' ? 'success' : d.route_b_status === 'contextual_only' ? 'warning' : 'muted'}>
                          {d.route_b_status === 'approved' ? 'Route B' : d.route_b_status === 'contextual_only' ? 'Contextual' : 'None'}
                        </Badge>
                      </td>
                      <td className="py-2 px-2 text-center text-xs">{d.model_family}</td>
                      <td className="py-2 px-2 text-center capitalize">{d.best_confidence}</td>
                      <td className="py-2 px-2 text-center capitalize">{d.best_transfer_risk}</td>
                      <td className="py-2 px-2 text-center">
                        {d.artifact_count}
                        {d.contextual_prior_count > 0 ? ` +${d.contextual_prior_count}c` : ''}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </Card>

      {cardsData?.model_cards && cardsData.model_cards.length > 0 && (
        <Card>
          <div className="p-4">
            <h3 className="font-semibold mb-3">{t('strengthOverview.models')}</h3>
            <div className="space-y-2">
              {cardsData.model_cards.map((card) => {
                const approval = card.approval_level as string || 'unapproved'
                const aClass = card.artifact_class as string || ''
                const strengthFromApproval =
                  aClass === 'calibrated_model' && approval === 'route_b_approved' ? 'strong_calibrated'
                  : aClass === 'data_backed_baseline' && approval === 'route_b_approved' ? 'data_backed'
                  : aClass ? 'contextual'
                  : 'none'
                return (
                  <div
                    key={card.model_id as string}
                    className="flex items-center justify-between p-3 rounded-lg"
                    style={{ backgroundColor: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
                  >
                    <div>
                      <span className="font-medium text-sm">{card.model_id as string}</span>
                      <span className="text-xs ml-2" style={{ color: 'var(--color-text-secondary)' }}>
                        {card.model_family as string}
                      </span>
                    </div>
                    <div className="flex gap-1.5">
                      <Badge variant={STRENGTH_BADGE[strengthFromApproval as StrengthLevel] || 'muted'}>
                        {t(`strengthOverview.levels.${strengthFromApproval}`)}
                      </Badge>
                      <Badge variant={approval === 'route_b_approved' ? 'success' : approval === 'lab_only' ? 'warning' : 'muted'}>
                        {approval}
                      </Badge>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </Card>
      )}

      {profilesData?.profiles && profilesData.profiles.length > 0 && (
        <Card>
          <div className="p-4">
            <h3 className="font-semibold mb-3">{t('strengthOverview.profiles')}</h3>
            <div className="space-y-2">
              {profilesData.profiles.map((profile) => (
                <div
                  key={profile.profile_id as string}
                  className="flex items-center justify-between p-3 rounded-lg"
                  style={{ backgroundColor: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
                >
                  <div>
                    <span className="font-medium text-sm">{profile.profile_id as string}</span>
                    <span className="text-xs ml-2" style={{ color: 'var(--color-text-secondary)' }}>
                      {(profile.domains as string[])?.join(', ')}
                    </span>
                  </div>
                  <Badge variant="info">{(profile.domains as string[])?.length ?? 0} domains</Badge>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {calibrationData?.records && calibrationData.records.length > 0 && (
        <Card>
          <div className="p-4">
            <h3 className="font-semibold mb-3">{t('strengthOverview.calibration')}</h3>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              {t('strengthOverview.calibrationSummary', { count: calibrationData.count })}
            </p>
          </div>
        </Card>
      )}
    </div>
  )
}

interface StrengthStats {
  strongCount: number
  dataBackedCount: number
  contextualCount: number
  noneCount: number
  approvedCount: number
  totalModels: number
  totalProfiles: number
  calibrationRecords: number
}

function SummaryStats({ stats }: { stats: StrengthStats }) {
  const { t } = useTranslation()
  const s = stats

  const items = [
    { label: t('strengthOverview.stats.strongModels'), value: s.strongCount, color: 'var(--color-success)' },
    { label: t('strengthOverview.stats.dataBacked'), value: s.dataBackedCount, color: 'var(--color-warning)' },
    { label: t('strengthOverview.stats.contextual'), value: s.contextualCount, color: 'var(--color-info)' },
    { label: t('strengthOverview.stats.noPrior'), value: s.noneCount, color: 'var(--color-text-secondary)' },
    { label: t('strengthOverview.stats.routeBApproved'), value: s.approvedCount, color: 'var(--color-accent)' },
    { label: t('strengthOverview.stats.totalModels'), value: s.totalModels, color: 'var(--color-accent)' },
    { label: t('strengthOverview.stats.profiles'), value: s.totalProfiles, color: 'var(--color-accent)' },
    { label: t('strengthOverview.stats.calibrationRecords'), value: s.calibrationRecords, color: 'var(--color-accent)' },
  ]

  return (
    <Card>
      <div className="p-4">
        <h3 className="font-semibold mb-3">{t('strengthOverview.stats.title')}</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {items.map((item) => (
            <div key={item.label} className="text-center">
              <div className="text-2xl font-bold" style={{ color: item.color }}>{item.value}</div>
              <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{item.label}</div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
