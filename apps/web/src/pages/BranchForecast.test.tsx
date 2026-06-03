import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import BranchForecast from './BranchForecast'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <BranchForecast />
    </QueryClientProvider>
  )
}

describe('BranchForecast', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('branchForecast.title')).toBeInTheDocument()
    expect(screen.getByText('branchForecast.description')).toBeInTheDocument()
  })

  it('shows analyze button', () => {
    renderPage()
    expect(screen.getByText('branchForecast.analyze')).toBeInTheDocument()
  })
})
