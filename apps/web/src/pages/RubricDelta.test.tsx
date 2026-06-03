import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import RubricDelta from './RubricDelta'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <RubricDelta />
    </QueryClientProvider>
  )
}

describe('RubricDelta', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('rubricDelta.title')).toBeInTheDocument()
    expect(screen.getByText('rubricDelta.description')).toBeInTheDocument()
  })

  it('shows generate button', () => {
    renderPage()
    expect(screen.getByText('rubricDelta.generate')).toBeInTheDocument()
  })
})
