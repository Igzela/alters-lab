import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useWeeklyReviews, useActionAlignmentScores, usePatternReviews, useProviderStatus } from '../hooks/useApi'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { SkeletonCard } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { useTheme } from '../components/ThemeContext'
import OnboardingModal, { shouldShowOnboarding } from '../components/OnboardingModal'

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function formatWeek(dateStr: string) {
  const d = new Date(dateStr)
  const start = new Date(d)
  start.setDate(d.getDate() - d.getDay())
  return `${start.getMonth() + 1}/${start.getDate()}`
}

export default function Dashboard() {
  const { t } = useTranslation()
  const { theme } = useTheme()
  const reviews = useWeeklyReviews()
  const scores = useActionAlignmentScores()
  const patterns = usePatternReviews()
  const providerStatus = useProviderStatus()
  const [showOnboarding, setShowOnboarding] = useState(shouldShowOnboarding)

  const isLoading = reviews.isLoading || scores.isLoading || patterns.isLoading
  const error = reviews.error || scores.error || patterns.error

  const textColor = theme === 'dark' ? '#a8a29e' : '#78716c'
  const borderColor = theme === 'dark' ? '#3a3a3a' : '#e8e6e1'

  const providerMode = (providerStatus.data as Record<string, unknown>)?.mode as string ?? t('dashboard.statusUnknown')
  const providerModeLabel = providerMode === 'disabled' ? t('dashboard.providerDisabled') : providerMode === 'mock' ? t('dashboard.providerMock') : providerMode === 'live' ? t('dashboard.providerLive') : providerMode
  const providerBadgeVariant = providerMode === 'live' ? 'success' : providerMode === 'mock' ? 'amber' : 'muted'

  const reviewCount = reviews.data?.count ?? 0
  const scoreCount = scores.data?.count ?? 0
  const patternCount = patterns.data?.reviews?.reduce(
    (sum: number, r: { triggered_patterns?: unknown[] }) => sum + (r.triggered_patterns?.length ?? 0), 0
  ) ?? 0

  const scoreData = (scores.data?.scores ?? [])
    .slice(-10)
    .map(s => ({
      date: formatDate(s.created_at),
      score: s.action_alignment_score,
    }))

  const weeklyData = (() => {
    const sessions = reviews.data?.sessions ?? []
    const byWeek = new Map<string, number>()
    for (const s of sessions) {
      const week = formatWeek(s.created_at)
      byWeek.set(week, (byWeek.get(week) ?? 0) + 1)
    }
    return Array.from(byWeek.entries()).slice(-8).map(([week, count]) => ({ week, count }))
  })()

  const latestPatterns = patterns.data?.reviews?.[0]?.triggered_patterns ?? []

  if (error) return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ color: 'var(--color-text)' }}>{t('dashboard.title')}</h2>
      <ErrorDisplay message={(error as Error).message} />
    </div>
  )

  if (isLoading) return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ color: 'var(--color-text)' }}>{t('dashboard.title')}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
      <SkeletonCard />
      <SkeletonCard />
    </div>
  )

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ color: 'var(--color-text)' }}>{t('dashboard.title')}</h2>

      {/* System health card */}
      <Card accent="blue">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium" style={{ color: 'var(--color-text)' }}>{t('dashboard.systemHealth')}</h3>
          <Badge variant={providerMode === 'disabled' ? 'muted' : 'success'}>{providerMode === 'disabled' ? t('dashboard.statusWarning') : t('dashboard.statusOk')}</Badge>
        </div>
        <div className="flex gap-6 mt-3">
          <div>
            <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{t('dashboard.providerMode')}</span>
            <div className="mt-1">
              <Badge variant={providerBadgeVariant}>{providerModeLabel}</Badge>
            </div>
          </div>
          <div>
            <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{t('dashboard.frontendStatus')}</span>
            <div className="mt-1">
              <Badge variant="success">{t('dashboard.statusOk')}</Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Summary counters */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: 'var(--color-accent)' }}>{reviewCount}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>{t('dashboard.weeklyReviews')}</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: 'var(--color-info)' }}>{scoreCount}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>{t('dashboard.alignmentScores')}</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: 'var(--color-success)' }}>{patternCount}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>{t('dashboard.patternsDetected')}</div>
          </div>
        </Card>
      </div>

      {/* Score trend */}
      <Card>
        <h3 className="text-sm font-medium mb-3" style={{ color: 'var(--color-text)' }}>{t('dashboard.scoreTrend')}</h3>
        {scoreData.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={scoreData}>
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: textColor }} stroke={borderColor} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 12, fill: textColor }} stroke={borderColor} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Line type="monotone" dataKey="score" stroke="#b45309" strokeWidth={2} dot={{ fill: '#b45309', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>{t('dashboard.noScores')}</p>
        )}
      </Card>

      {/* Weekly activity */}
      <Card>
        <h3 className="text-sm font-medium mb-3" style={{ color: 'var(--color-text)' }}>{t('dashboard.weeklyActivity')}</h3>
        {weeklyData.length > 0 ? (
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={weeklyData}>
              <XAxis dataKey="week" tick={{ fontSize: 12, fill: textColor }} stroke={borderColor} />
              <YAxis tick={{ fontSize: 12, fill: textColor }} stroke={borderColor} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>{t('dashboard.noData')}</p>
        )}
      </Card>

      {/* Recent patterns */}
      <Card>
        <h3 className="text-sm font-medium mb-3" style={{ color: 'var(--color-text)' }}>{t('dashboard.recentPatterns')}</h3>
        {latestPatterns.length > 0 ? (
          <div className="space-y-2">
            {latestPatterns.map((p: { pattern: string; occurrences: number; confidence: number }, i: number) => (
              <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg" style={{ backgroundColor: 'var(--color-surface-raised)' }}>
                <span className="text-sm font-medium" style={{ color: 'var(--color-text)' }}>{p.pattern}</span>
                <div className="flex items-center gap-2">
                  <Badge variant="info">{p.occurrences}x</Badge>
                  <Badge variant="amber">{Math.round(p.confidence * 100)}%</Badge>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>{t('dashboard.noPatterns')}</p>
        )}
      </Card>

      {showOnboarding && <OnboardingModal onClose={() => setShowOnboarding(false)} />}
    </div>
  )
}
