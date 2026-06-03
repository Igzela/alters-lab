import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import P6Progress from './P6Progress'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <P6Progress />
    </QueryClientProvider>
  )
}

describe('P6Progress', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4, .rounded-xl')).toBeTruthy()
  })

  it('shows title', () => {
    renderPage()
    expect(screen.getByText('progress.title')).toBeInTheDocument()
  })

  it('shows progress stats', () => {
    renderPage()
    expect(screen.getByText('progress.weeklyNotesIngested')).toBeInTheDocument()
    expect(screen.getByText('progress.weeklyReviewsCompleted')).toBeInTheDocument()
    expect(screen.getByText('progress.alignmentScoresRecorded')).toBeInTheDocument()
  })
})
