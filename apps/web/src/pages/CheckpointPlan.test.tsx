import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import CheckpointPlan from './CheckpointPlan'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <CheckpointPlan />
    </QueryClientProvider>
  )
}

describe('CheckpointPlan', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('checkpointPlan.title')).toBeInTheDocument()
    expect(screen.getByText('checkpointPlan.description')).toBeInTheDocument()
  })

  it('shows generate button', () => {
    renderPage()
    expect(screen.getByText('checkpointPlan.generate')).toBeInTheDocument()
  })
})
