import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Card } from './Card'

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Content</Card>)
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('applies default variant styles', () => {
    render(<Card>Content</Card>)
    const card = screen.getByText('Content').closest('div')
    expect(card).toHaveStyle({ backgroundColor: '#ffffff' })
  })

  it('applies raised variant styles', () => {
    render(<Card variant="raised">Content</Card>)
    const card = screen.getByText('Content').closest('div')
    expect(card).toHaveStyle({ backgroundColor: '#f5f4f0' })
  })

  it('applies accent border when specified', () => {
    render(<Card accent="amber">Content</Card>)
    const card = screen.getByText('Content').closest('div')
    expect(card).toHaveStyle({ borderLeft: '3px solid #b45309' })
  })
})
