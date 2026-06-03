import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import '../test/mocks'

vi.mock('../components/NavigationContext', () => ({
  useNavigation: () => ({ currentPage: 'getting-started' as const, navigate: vi.fn() }),
  NavigationProvider: ({ children }: { children: React.ReactNode }) => children,
}))

import GettingStarted from './GettingStarted'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <GettingStarted />
    </QueryClientProvider>
  )
}

describe('GettingStarted', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title', () => {
    renderPage()
    expect(screen.getByText('gettingStarted.title')).toBeInTheDocument()
  })

  it('shows onboarding steps', () => {
    renderPage()
    expect(screen.getByText('gettingStarted.step1Title')).toBeInTheDocument()
    expect(screen.getByText('gettingStarted.step2Title')).toBeInTheDocument()
    expect(screen.getByText('gettingStarted.step3Title')).toBeInTheDocument()
  })
})
