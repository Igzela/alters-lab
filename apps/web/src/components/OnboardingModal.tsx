import { useEffect, useRef, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { X } from '@phosphor-icons/react'
import { expandIn, pulseSuccess } from '../animations'
import { Button } from './Button'
import { Card } from './Card'
import { ProgressBar } from './ProgressBar'
import { useNavigation } from './NavigationContext'
import type { Page } from '../types'

const STORAGE_KEY = 'alters_lab_onboarding_steps'
const DISMISSED_KEY = 'alters_lab_onboarding_dismissed'
const TOTAL_STEPS = 5

function loadCompleted(): Set<number> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return new Set(JSON.parse(raw))
  } catch {}
  return new Set()
}

function saveCompleted(steps: Set<number>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...steps]))
}

function isOnboardingComplete(): boolean {
  return loadCompleted().size >= TOTAL_STEPS
}

function isDismissed(): boolean {
  return localStorage.getItem(DISMISSED_KEY) === 'true'
}

export function shouldShowOnboarding(): boolean {
  return !isOnboardingComplete() && !isDismissed()
}

export default function OnboardingModal({ onClose }: { onClose: () => void }) {
  const { t } = useTranslation()
  const { navigate } = useNavigation()
  const [completed, setCompleted] = useState<Set<number>>(loadCompleted)
  const [expanded, setExpanded] = useState<number | null>(1)
  const stepRefs = useRef<Map<number, HTMLDivElement>>(new Map())
  const backdropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (expanded !== null) {
      const el = stepRefs.current.get(expanded)
      if (el) expandIn(el)
    }
  }, [expanded])

  const handleClose = useCallback(() => {
    localStorage.setItem(DISMISSED_KEY, 'true')
    onClose()
  }, [onClose])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [handleClose])

  const toggleStep = (step: number) => {
    setExpanded(expanded === step ? null : step)
  }

  const markComplete = (step: number) => {
    const next = new Set(completed)
    if (next.has(step)) {
      next.delete(step)
    } else {
      next.add(step)
    }
    setCompleted(next)
    saveCompleted(next)
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === backdropRef.current) handleClose()
  }

  const steps = [
    {
      id: 1,
      title: t('gettingStarted.step1Title'),
      desc: t('gettingStarted.step1Desc'),
      action: t('gettingStarted.step1Action'),
      navigate: 'data' as Page,
    },
    {
      id: 2,
      title: t('gettingStarted.step2Title'),
      desc: t('gettingStarted.step2Desc'),
      action: t('gettingStarted.step2Action'),
      navigate: 'status' as Page,
    },
    {
      id: 3,
      title: t('gettingStarted.step3Title'),
      desc: t('gettingStarted.step3Desc'),
      action: t('gettingStarted.step3Action'),
      navigate: 'provider' as Page,
    },
    {
      id: 4,
      title: t('gettingStarted.step4Title'),
      desc: t('gettingStarted.step4Desc'),
      action: t('gettingStarted.step4Action'),
      navigate: 'weekly' as Page,
    },
    {
      id: 5,
      title: t('gettingStarted.step5Title'),
      desc: t('gettingStarted.step5Desc'),
      action: t('gettingStarted.step5Action'),
      navigate: null,
    },
  ]

  const doneCount = completed.size

  return (
    <div
      ref={backdropRef}
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', backdropFilter: 'blur(4px)' }}
      role="dialog"
      aria-modal="true"
      aria-label={t('gettingStarted.welcomeTitle')}
      aria-describedby="onboarding-subtitle"
    >
      <div
        className="w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-2xl p-5 space-y-4"
        style={{ backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}
      >
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight" style={{ color: 'var(--color-text)' }}>
              {t('gettingStarted.welcomeTitle')}
            </h2>
            <p id="onboarding-subtitle" className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
              {t('gettingStarted.welcomeSubtitle')}
            </p>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 rounded-lg transition-colors border-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]"
            style={{ color: 'var(--color-text-muted)', backgroundColor: 'transparent' }}
            aria-label={t('gettingStarted.closeOnboarding')}
          >
            <X size={20} />
          </button>
        </div>

        {/* Progress */}
        <Card>
          <p className="text-sm mb-2" style={{ color: 'var(--color-text-secondary)' }}>
            {t('gettingStarted.progress')} {doneCount}/{steps.length}
          </p>
          <ProgressBar value={doneCount} max={steps.length} accent="amber" />
        </Card>

        {/* Steps */}
        {steps.map(step => (
          <div
            key={step.id}
            className="rounded-xl overflow-hidden transition-all duration-200"
            style={{
              backgroundColor: completed.has(step.id) ? 'var(--color-success-light)' : 'var(--color-surface)',
              border: completed.has(step.id)
                ? '1px solid var(--color-success-light)'
                : '1px solid var(--color-border)',
            }}
          >
            <button
              className="w-full px-4 py-3 flex items-center gap-3 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2"
              style={{ backgroundColor: 'transparent' }}
              onClick={() => toggleStep(step.id)}
              aria-expanded={expanded === step.id}
              aria-controls={`modal-step-content-${step.id}`}
            >
              <span
                className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0"
                style={{
                  backgroundColor: completed.has(step.id) ? 'var(--color-success)' : 'var(--color-surface-raised)',
                  color: completed.has(step.id) ? 'var(--color-surface)' : 'var(--color-text-secondary)',
                }}
              >
                {completed.has(step.id) ? '✓' : step.id}
              </span>
              <span className="text-sm font-medium flex-1" style={{ color: completed.has(step.id) ? 'var(--color-success)' : 'var(--color-text)' }}>
                {step.title}
              </span>
              <svg
                className="w-4 h-4 transition-transform duration-200 flex-shrink-0"
                style={{ color: 'var(--color-text-muted)', transform: expanded === step.id ? 'rotate(180deg)' : 'rotate(0deg)' }}
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
              </svg>
            </button>

            {expanded === step.id && (
              <div ref={el => { if (el) stepRefs.current.set(step.id, el) }} id={`modal-step-content-${step.id}`} role="region" className="px-4 pb-4 pt-1 space-y-3">
                <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>{step.desc}</p>
                <div className="flex gap-2">
                  {step.navigate && (
                    <Button variant="secondary" onClick={() => { navigate(step.navigate!); handleClose() }}>
                      {step.action}
                    </Button>
                  )}
                  <Button
                    variant={completed.has(step.id) ? 'ghost' : 'primary'}
                    onClick={(e) => {
                      markComplete(step.id)
                      if (!completed.has(step.id)) pulseSuccess(e.currentTarget)
                    }}
                  >
                    {completed.has(step.id) ? t('gettingStarted.markIncomplete') : t('gettingStarted.markComplete')}
                  </Button>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Safety note */}
        <Card>
          <h3 className="text-sm font-medium mb-2">{t('gettingStarted.boundaries')}</h3>
          <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
            <strong style={{ color: 'var(--color-text)' }}>{t('gettingStarted.providerOutput')}</strong> {t('gettingStarted.providerOutputDesc')}
          </p>
        </Card>

        {/* Close button at bottom */}
        <div className="flex justify-end pt-2">
          <Button variant="ghost" onClick={handleClose}>
            {t('gettingStarted.closeOnboarding')}
          </Button>
        </div>
      </div>
    </div>
  )
}
