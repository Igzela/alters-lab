import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import '../test/mocks'

vi.mock('../components/Toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
  ToastProvider: ({ children }: { children: React.ReactNode }) => children,
}))

import ProviderSettings from './ProviderSettings'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <ProviderSettings />
    </QueryClientProvider>
  )
}

describe('ProviderSettings', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title', () => {
    renderPage()
    expect(screen.getByText('provider.title')).toBeInTheDocument()
  })

  it('shows safety notes', () => {
    renderPage()
    expect(screen.getByText('provider.safetyNotes')).toBeInTheDocument()
  })
})
