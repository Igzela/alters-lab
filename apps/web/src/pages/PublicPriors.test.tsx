import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { describe, it, expect } from 'vitest'
import i18n from '../i18n'
import PublicPriors from './PublicPriors'

function renderAt() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter initialEntries={['/public-priors']}>
      <I18nextProvider i18n={i18n}>
        <QueryClientProvider client={qc}>
          <PublicPriors />
        </QueryClientProvider>
      </I18nextProvider>
    </MemoryRouter>,
  )
}

describe('PublicPriors', () => {
  it('renders without crashing', () => {
    renderAt()
    expect(screen.getByText(/Public Priors/i)).toBeTruthy()
  })

  it('shows title and description', () => {
    renderAt()
    expect(screen.getByText('Public Priors')).toBeTruthy()
    expect(screen.getByText(/Population baseline priors/i)).toBeTruthy()
  })

  it('shows tab navigation', () => {
    renderAt()
    expect(screen.getByText('Domain Coverage')).toBeTruthy()
    expect(screen.getByText('Prior Artifacts')).toBeTruthy()
    expect(screen.getByText('Model Cards')).toBeTruthy()
  })
})
