import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import StrengthOverview from './StrengthOverview'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <StrengthOverview />
    </QueryClientProvider>
  )
}

describe('StrengthOverview', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('strengthOverview.title')).toBeInTheDocument()
    expect(screen.getByText('strengthOverview.description')).toBeInTheDocument()
  })

  it('shows domain matrix table', () => {
    renderPage()
    expect(screen.getByText('strengthOverview.domainMatrix')).toBeInTheDocument()
    expect(screen.getByText('strengthOverview.domain')).toBeInTheDocument()
    expect(screen.getByText('strengthOverview.strengthLevel')).toBeInTheDocument()
  })
})
