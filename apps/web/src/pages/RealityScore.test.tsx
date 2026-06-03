import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import '../test/mocks'

vi.mock('../components/NavigationContext', () => ({
  useNavigation: () => ({ currentPage: 'reality-score' as const, navigate: vi.fn() }),
  NavigationProvider: ({ children }: { children: React.ReactNode }) => children,
}))

import RealityScore from './RealityScore'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <RealityScore />
    </QueryClientProvider>
  )
}

describe('RealityScore', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('realityScore.title')).toBeInTheDocument()
    expect(screen.getByText('realityScore.description')).toBeInTheDocument()
  })

  it('shows submit button', () => {
    renderPage()
    expect(screen.getByText('realityScore.submitScore')).toBeInTheDocument()
  })
})
