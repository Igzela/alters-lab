import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import ForecastCalibration from './ForecastCalibration'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <ForecastCalibration />
    </QueryClientProvider>
  )
}

describe('ForecastCalibration', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('forecastCalibration.title')).toBeInTheDocument()
    expect(screen.getByText('forecastCalibration.description')).toBeInTheDocument()
  })

  it('shows tab buttons', () => {
    renderPage()
    expect(screen.getByText('forecastCalibration.tabs.snapshots')).toBeInTheDocument()
    expect(screen.getByText('forecastCalibration.tabs.evidence')).toBeInTheDocument()
    expect(screen.getByText('forecastCalibration.tabs.evaluations')).toBeInTheDocument()
    expect(screen.getByText('forecastCalibration.tabs.scorecard')).toBeInTheDocument()
  })
})
