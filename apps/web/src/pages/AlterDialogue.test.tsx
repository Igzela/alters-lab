import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import '../test/mocks'
import AlterDialogue from './AlterDialogue'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <AlterDialogue />
    </QueryClientProvider>
  )
}

describe('AlterDialogue', () => {
  it('renders without crashing', () => {
    renderPage()
    expect(document.querySelector('.space-y-4')).toBeTruthy()
  })

  it('shows title and description', () => {
    renderPage()
    expect(screen.getByText('dialogue.title')).toBeInTheDocument()
    expect(screen.getByText('dialogue.description')).toBeInTheDocument()
  })

  it('shows send button and alter selector', () => {
    renderPage()
    expect(screen.getByText('dialogue.send')).toBeInTheDocument()
  })
})
