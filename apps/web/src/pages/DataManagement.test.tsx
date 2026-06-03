import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import '../test/mocks'
import DataManagement from './DataManagement'

vi.mock('../components/Toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
  ToastProvider: ({ children }: { children: React.ReactNode }) => children,
}))

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <DataManagement />
    </QueryClientProvider>
  )
}

describe('DataManagement', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('data.title')).toBeInTheDocument()
    expect(screen.getByText('data.description')).toBeInTheDocument()
  })

  it('shows delete by ID section', () => {
    renderPage()
    expect(screen.getByText('data.deleteById')).toBeInTheDocument()
  })
})
