import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { NavigationProvider, useNavigation } from './NavigationContext'

function TestConsumer() {
  const { currentPage, navigate } = useNavigation()
  return (
    <div>
      <span data-testid="page">{currentPage}</span>
      <button onClick={() => navigate('weekly')}>go weekly</button>
    </div>
  )
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <NavigationProvider>
        <TestConsumer />
      </NavigationProvider>
    </MemoryRouter>,
  )
}

describe('NavigationProvider', () => {
  it('defaults to dashboard for root path', () => {
    renderAt('/')
    expect(screen.getByTestId('page').textContent).toBe('dashboard')
  })

  it('resolves page from path', () => {
    renderAt('/weekly')
    expect(screen.getByTestId('page').textContent).toBe('weekly')
  })

  it('falls back to dashboard for unknown paths', () => {
    renderAt('/nonexistent')
    expect(screen.getByTestId('page').textContent).toBe('dashboard')
  })
})
