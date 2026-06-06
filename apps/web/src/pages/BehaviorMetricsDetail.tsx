import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { useBehaviorMetricsRecords } from '../hooks/useApi'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Skeleton } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'

const METRIC_IDS = [
  'career_education_deep_work_minutes',
  'planned_commitment_follow_through_rate',
  'expense_logged_days',
  'regular_sleep_nights',
  'moderate_vigorous_activity_minutes',
  'avoidable_health_risk_events',
  'meaningful_social_contact_count',
  'abandoned_committed_blocks',
  'key_milestone_progress_pct',
] as const

type MetricId = (typeof METRIC_IDS)[number]

interface BehaviorRecord {
  record_id: string
  week_start: string
  week_end: string
  [key: string]: unknown
}

function formatMetricValue(id: MetricId, record: BehaviorRecord): string {
  const raw = record[id]
  if (raw == null) return '-'
  if (id === 'planned_commitment_follow_through_rate' || id === 'key_milestone_progress_pct') {
    return `${(Number(raw) * 100).toFixed(0)}%`
  }
  return String(raw)
}

function getNumericValue(id: MetricId, record: BehaviorRecord): number | null {
  const raw = record[id]
  if (raw == null) return null
  const n = Number(raw)
  if (id === 'planned_commitment_follow_through_rate' || id === 'key_milestone_progress_pct') {
    return n * 100
  }
  return n
}

type TrendDirection = 'up' | 'down' | 'stable' | 'first'

function computeTrend(
  id: MetricId,
  records: BehaviorRecord[],
): TrendDirection {
  if (records.length < 2) return 'first'
  const sorted = [...records].sort(
    (a, b) => new Date(a.week_start).getTime() - new Date(b.week_start).getTime(),
  )
  const recent = sorted.slice(-4)
  if (recent.length < 2) return 'first'

  const values = recent
    .map(r => getNumericValue(id, r))
    .filter((v): v is number => v != null)

  if (values.length < 2) return 'first'

  const first = values[0]
  const last = values[values.length - 1]
  const diff = last - first
  const threshold = Math.abs(first) * 0.1

  if (Math.abs(diff) < threshold) return 'stable'

  // For "bad" metrics (higher = worse), invert the direction
  const lowerIsBetter =
    id === 'expense_logged_days' ||
    id === 'avoidable_health_risk_events' ||
    id === 'abandoned_committed_blocks'

  if (lowerIsBetter) {
    return diff < 0 ? 'up' : 'down'
  }
  return diff > 0 ? 'up' : 'down'
}

function TrendBadge({ direction, t }: { direction: TrendDirection; t: (key: string) => string }) {
  if (direction === 'first') {
    return <Badge variant="muted">{t('behaviorMetrics.noPriorWeeks')}</Badge>
  }
  const variant = direction === 'up' ? 'success' : direction === 'down' ? 'error' : 'muted'
  const label =
    direction === 'up'
      ? t('behaviorMetrics.trendUp')
      : direction === 'down'
        ? t('behaviorMetrics.trendDown')
        : t('behaviorMetrics.trendStable')
  return <Badge variant={variant}>{label}</Badge>
}

function TrendSparkline({
  id,
  records,
}: {
  id: MetricId
  records: BehaviorRecord[]
}) {
  const sorted = [...records]
    .sort((a, b) => new Date(a.week_start).getTime() - new Date(b.week_start).getTime())
    .slice(-4)

  const values = sorted
    .map(r => getNumericValue(id, r))
    .filter((v): v is number => v != null)

  if (values.length < 2) return null

  const max = Math.max(...values)
  const min = Math.min(...values)
  const range = max - min || 1
  const width = 80
  const height = 24
  const padding = 2

  const points = values
    .map((v, i) => {
      const x = padding + (i / (values.length - 1)) * (width - 2 * padding)
      const y = height - padding - ((v - min) / range) * (height - 2 * padding)
      return `${x},${y}`
    })
    .join(' ')

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline
        points={points}
        fill="none"
        stroke="var(--color-accent)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function BehaviorMetricsDetail() {
  const { t } = useTranslation()
  const recordsQuery = useBehaviorMetricsRecords()

  const records = useMemo(() => {
    const data = recordsQuery.data as { records: BehaviorRecord[] } | undefined
    return data?.records ?? []
  }, [recordsQuery.data])

  const sortedRecords = useMemo(
    () =>
      [...records].sort(
        (a, b) => new Date(b.week_start).getTime() - new Date(a.week_start).getTime(),
      ),
    [records],
  )

  const currentWeek = sortedRecords[0] ?? null

  const trendData = useMemo(() => {
    const result: Partial<Record<MetricId, TrendDirection>> = {}
    for (const id of METRIC_IDS) {
      result[id] = computeTrend(id, records)
    }
    return result
  }, [records])

  if (recordsQuery.isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-bold tracking-tight">{t('behaviorMetrics.title')}</h2>
        <Skeleton lines={6} className="h-48" />
      </div>
    )
  }

  if (recordsQuery.error) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-bold tracking-tight">{t('behaviorMetrics.title')}</h2>
        <ErrorDisplay message={(recordsQuery.error as Error).message} onRetry={() => recordsQuery.refetch()} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('behaviorMetrics.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
        {t('behaviorMetrics.description')}
      </p>

      {sortedRecords.length === 0 ? (
        <Card>
          <div className="p-4 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {t('behaviorMetrics.noData')}
          </div>
        </Card>
      ) : (
        <>
          {/* Current week header */}
          <Card accent="amber">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-semibold">{t('behaviorMetrics.currentWeek')}</h3>
              <Badge variant="amber">
                {t('behaviorMetrics.weekCount', { count: sortedRecords.length })}
              </Badge>
            </div>
            {currentWeek && (
              <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                {t('behaviorMetrics.weekOf')}: {currentWeek.week_start} &mdash; {currentWeek.week_end}
              </p>
            )}
          </Card>

          {/* Metrics grid */}
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <th className="text-left py-2 px-2 font-medium">{t('behaviorMetrics.metric')}</th>
                    <th className="text-right py-2 px-2 font-medium">{t('behaviorMetrics.value')}</th>
                    <th className="text-center py-2 px-2 font-medium">{t('behaviorMetrics.unit')}</th>
                    <th className="text-center py-2 px-2 font-medium">{t('behaviorMetrics.trend')}</th>
                  </tr>
                </thead>
                <tbody>
                  {METRIC_IDS.map(id => (
                    <tr key={id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td className="py-2 px-2 font-medium">
                        {t(`behaviorMetrics.metrics.${id}`)}
                      </td>
                      <td className="py-2 px-2 text-right font-mono">
                        {currentWeek ? formatMetricValue(id, currentWeek) : '-'}
                      </td>
                      <td className="py-2 px-2 text-center text-xs" style={{ color: 'var(--color-text-muted)' }}>
                        {t(`behaviorMetrics.units.${id}`)}
                      </td>
                      <td className="py-2 px-2 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <TrendSparkline id={id} records={sortedRecords} />
                          <TrendBadge direction={trendData[id] ?? 'first'} t={t} />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Recent weeks summary */}
          {sortedRecords.length > 1 && (
            <Card>
              <h3 className="font-semibold mb-3">{t('behaviorMetrics.trend')}</h3>
              <div className="space-y-2">
                {sortedRecords.slice(0, 4).map(record => (
                  <div
                    key={record.record_id}
                    className="flex items-center justify-between p-2 rounded text-xs"
                    style={{ backgroundColor: 'var(--color-surface-raised)' }}
                  >
                    <span style={{ color: 'var(--color-text-secondary)' }}>
                      {record.week_start} &mdash; {record.week_end}
                    </span>
                    <div className="flex gap-3 font-mono">
                      <span title={t('behaviorMetrics.metrics.career_education_deep_work_minutes')}>
                        DW: {formatMetricValue('career_education_deep_work_minutes', record)}
                      </span>
                      <span title={t('behaviorMetrics.metrics.regular_sleep_nights')}>
                        SL: {formatMetricValue('regular_sleep_nights', record)}
                      </span>
                      <span title={t('behaviorMetrics.metrics.moderate_vigorous_activity_minutes')}>
                        EX: {formatMetricValue('moderate_vigorous_activity_minutes', record)}
                      </span>
                      <span title={t('behaviorMetrics.metrics.meaningful_social_contact_count')}>
                        SC: {formatMetricValue('meaningful_social_contact_count', record)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
