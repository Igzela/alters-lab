import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import PredictorProfile from './PredictorProfile'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <PredictorProfile />
    </QueryClientProvider>
  )
}

describe('PredictorProfile', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('predictorProfile.title')).toBeInTheDocument()
    expect(screen.getByText('predictorProfile.description')).toBeInTheDocument()
  })

  it('shows create button', () => {
    renderPage()
    expect(screen.getByText('predictorProfile.create')).toBeInTheDocument()
  })
})
