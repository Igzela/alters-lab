import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import '../test/mocks'

vi.mock('../components/NavigationContext', () => ({
  useNavigation: () => ({ currentPage: 'status' as const, navigate: vi.fn() }),
  NavigationProvider: ({ children }: { children: React.ReactNode }) => children,
}))

import SystemStatus from './SystemStatus'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <SystemStatus />
    </QueryClientProvider>
  )
}

describe('SystemStatus', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title', () => {
    renderPage()
    expect(screen.getByText('status.title')).toBeInTheDocument()
  })

  it('shows local app and product surface cards', () => {
    renderPage()
    expect(screen.getByText('status.localApp')).toBeInTheDocument()
    expect(screen.getByText('status.productSurface')).toBeInTheDocument()
  })
})
