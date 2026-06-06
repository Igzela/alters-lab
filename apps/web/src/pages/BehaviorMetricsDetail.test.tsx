import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { I18nextProvider } from 'react-i18next'
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import BehaviorMetricsDetail from './BehaviorMetricsDetail'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Minimal i18n setup
i18n.use(initReactI18next).init({
  lng: 'en',
  resources: {
    en: {
      translation: {
        'behaviorMetrics.title': 'Behavior Metrics',
        'behaviorMetrics.description': 'Current week behavior metrics with 4-week trend.',
        'behaviorMetrics.currentWeek': 'Current Week',
        'behaviorMetrics.noData': 'No behavior metrics recorded yet.',
        'behaviorMetrics.metric': 'Metric',
        'behaviorMetrics.value': 'Value',
        'behaviorMetrics.unit': 'Unit',
        'behaviorMetrics.trend': '4-Week Trend',
        'behaviorMetrics.loading': 'Loading behavior metrics...',
        'behaviorMetrics.weekOf': 'Week of',
        'behaviorMetrics.weekCount': '{{count}} week recorded',
        'behaviorMetrics.noPriorWeeks': 'First week recorded',
        'behaviorMetrics.trendUp': 'Improving',
        'behaviorMetrics.trendDown': 'Declining',
        'behaviorMetrics.trendStable': 'Stable',
        'behaviorMetrics.metrics.career_education_deep_work_minutes': 'Deep Work',
        'behaviorMetrics.metrics.planned_commitment_follow_through_rate': 'Follow-Through Rate',
        'behaviorMetrics.metrics.expense_logged_days': 'Overspending Days',
        'behaviorMetrics.metrics.regular_sleep_nights': 'Good Sleep Nights',
        'behaviorMetrics.metrics.moderate_vigorous_activity_minutes': 'Exercise',
        'behaviorMetrics.metrics.avoidable_health_risk_events': 'Health Risk Events',
        'behaviorMetrics.metrics.meaningful_social_contact_count': 'Social Contacts',
        'behaviorMetrics.metrics.abandoned_committed_blocks': 'Abandoned Time Blocks',
        'behaviorMetrics.metrics.key_milestone_progress_pct': 'Milestone Progress',
        'behaviorMetrics.units.career_education_deep_work_minutes': 'min',
        'behaviorMetrics.units.planned_commitment_follow_through_rate': '%',
        'behaviorMetrics.units.expense_logged_days': 'days',
        'behaviorMetrics.units.regular_sleep_nights': 'nights',
        'behaviorMetrics.units.moderate_vigorous_activity_minutes': 'min',
        'behaviorMetrics.units.avoidable_health_risk_events': 'events',
        'behaviorMetrics.units.meaningful_social_contact_count': 'contacts',
        'behaviorMetrics.units.abandoned_committed_blocks': 'blocks',
        'behaviorMetrics.units.key_milestone_progress_pct': '%',
        'common.loading': 'Loading...',
      },
    },
  },
})

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <I18nextProvider i18n={i18n}>{children}</I18nextProvider>
      </QueryClientProvider>
    )
  }
}

describe('BehaviorMetricsDetail', () => {
  beforeEach(() => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ status: 'ok', records: [], count: 0 }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the page title', async () => {
    render(<BehaviorMetricsDetail />, { wrapper: createWrapper() })
    expect(screen.getByText('Behavior Metrics')).toBeDefined()
  })

  it('shows the description text', async () => {
    render(<BehaviorMetricsDetail />, { wrapper: createWrapper() })
    const desc = await screen.findByText(
      'Current week behavior metrics with 4-week trend.',
    )
    expect(desc).toBeDefined()
  })

  it('shows empty state when no records exist', async () => {
    render(<BehaviorMetricsDetail />, { wrapper: createWrapper() })
    // Wait for the query to resolve
    const emptyMsg = await screen.findByText(
      'No behavior metrics recorded yet.',
    )
    expect(emptyMsg).toBeDefined()
  })
})
