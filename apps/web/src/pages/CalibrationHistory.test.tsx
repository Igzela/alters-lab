import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import CalibrationHistory from './CalibrationHistory'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <CalibrationHistory />
    </QueryClientProvider>
  )
}

describe('CalibrationHistory', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('displays the page title', () => {
    renderPage()
    expect(screen.getByText('history.title')).toBeInTheDocument()
  })

  it('shows empty state when no records', () => {
    renderPage()
    expect(screen.getByText('history.noRecords')).toBeInTheDocument()
  })
})
