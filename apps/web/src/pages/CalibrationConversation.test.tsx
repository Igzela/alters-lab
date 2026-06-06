import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import CalibrationConversation from './CalibrationConversation'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <CalibrationConversation />
    </QueryClientProvider>
  )
}

describe('CalibrationConversation', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('calConversation.title')).toBeInTheDocument()
    expect(screen.getByText('calConversation.description')).toBeInTheDocument()
  })

  it('shows start button', () => {
    renderPage()
    expect(screen.getByText('calConversation.start')).toBeInTheDocument()
  })
})
