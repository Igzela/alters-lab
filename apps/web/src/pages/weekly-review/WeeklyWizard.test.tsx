import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import '../../test/mocks'
import WeeklyWizard from './WeeklyWizard'

vi.mock('../../api', () => ({
  fetchJson: vi.fn().mockResolvedValue({ alters: [] }),
  ingestWeeklyNote: vi.fn(),
  editWeeklyNote: vi.fn(),
  startWeeklyReview: vi.fn(),
  completeWeeklyReview: vi.fn(),
  scoreActionAlignment: vi.fn(),
  suggestWeeklyReviewAssistant: vi.fn(),
  fetchWeeklyReviewAssistantStatus: vi.fn(),
}))

function renderWizard() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <WeeklyWizard />
    </QueryClientProvider>
  )
}

describe('WeeklyWizard', () => {
  it('renders without crashing', () => {
    renderWizard()
    expect(screen.getByText('weeklyReview.title')).toBeInTheDocument()
  })

  it('shows step 1 of 6', () => {
    renderWizard()
    expect(screen.getByText('1/6')).toBeInTheDocument()
  })

  it('displays all step buttons', () => {
    renderWizard()
    expect(screen.getByText('weeklyReview.step1')).toBeInTheDocument()
    expect(screen.getByText('weeklyReview.step6')).toBeInTheDocument()
  })

  it('shows step description', () => {
    renderWizard()
    expect(screen.getByText('weeklyReview.description')).toBeInTheDocument()
  })
})
