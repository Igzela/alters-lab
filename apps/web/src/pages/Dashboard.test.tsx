import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import Dashboard from './Dashboard'

function renderDashboard() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <Dashboard />
    </QueryClientProvider>
  )
}

describe('Dashboard', () => {
  it('renders without crashing', () => {
    renderDashboard()
    expect(screen.getByText('dashboard.title')).toBeInTheDocument()
  })

  it('shows summary stats', () => {
    renderDashboard()
    expect(screen.getByText('dashboard.weeklyReviews')).toBeInTheDocument()
    expect(screen.getByText('dashboard.alignmentScores')).toBeInTheDocument()
    expect(screen.getByText('dashboard.patternsDetected')).toBeInTheDocument()
  })

  it('shows chart sections', () => {
    renderDashboard()
    expect(screen.getByText('dashboard.scoreTrend')).toBeInTheDocument()
    expect(screen.getByText('dashboard.weeklyActivity')).toBeInTheDocument()
  })
})
