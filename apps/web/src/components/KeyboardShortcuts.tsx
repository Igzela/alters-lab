import { useEffect, useRef, useState } from 'react'
import type { Page } from '../types'
import ShortcutHelp from './ShortcutHelp'

const SHORTCUTS: Record<string, Page> = {
  d: 'dashboard',
  s: 'status',
  w: 'weekly',
  r: 'reality',
  h: 'history',
  p: 'patterns',
  c: 'checkpoint',
  a: 'dialogue',
  v: 'validation',
  t: 'provider',
}

interface KeyboardShortcutsProps {
  onNavigate: (page: Page) => void
}

export default function KeyboardShortcuts({ onNavigate }: KeyboardShortcutsProps) {
  const [showHelp, setShowHelp] = useState(false)
  const pendingRef = useRef(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) return
      if (e.metaKey || e.ctrlKey || e.altKey) return

      if (e.key === '?') {
        e.preventDefault()
        setShowHelp(v => !v)
        return
      }

      if (e.key === 'Escape') {
        setShowHelp(false)
        pendingRef.current = false
        clearTimeout(timeoutRef.current)
        return
      }

      if (pendingRef.current) {
        pendingRef.current = false
        clearTimeout(timeoutRef.current)
        const page = SHORTCUTS[e.key]
        if (page) {
          e.preventDefault()
          onNavigate(page)
        }
        return
      }

      if (e.key === 'g') {
        pendingRef.current = true
        timeoutRef.current = setTimeout(() => {
          pendingRef.current = false
        }, 1000)
        return
      }
    }

    window.addEventListener('keydown', handler)
    return () => {
      window.removeEventListener('keydown', handler)
      clearTimeout(timeoutRef.current)
    }
  }, [onNavigate])

  return showHelp ? <ShortcutHelp onClose={() => setShowHelp(false)} /> : null
}
