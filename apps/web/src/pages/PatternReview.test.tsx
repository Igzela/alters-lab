import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import PatternReview from './PatternReview'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <PatternReview />
    </QueryClientProvider>
  )
}

describe('PatternReview', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('patterns.title')).toBeInTheDocument()
    expect(screen.getByText('patterns.description')).toBeInTheDocument()
  })

  it('shows build new button', () => {
    renderPage()
    expect(screen.getByText('patterns.buildNew')).toBeInTheDocument()
  })
})
