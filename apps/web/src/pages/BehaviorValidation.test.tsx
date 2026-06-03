import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import BehaviorValidation from './BehaviorValidation'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <BehaviorValidation />
    </QueryClientProvider>
  )
}

describe('BehaviorValidation', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('validation.title')).toBeInTheDocument()
    expect(screen.getByText('validation.description')).toBeInTheDocument()
  })

  it('shows run evaluation button', () => {
    renderPage()
    expect(screen.getByText('validation.runEvaluation')).toBeInTheDocument()
  })
})
