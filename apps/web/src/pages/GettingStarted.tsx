import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { expandIn, pulseSuccess } from '../animations'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { ProgressBar } from '../components/ProgressBar'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started' | 'patterns' | 'validation' | 'data'

const STORAGE_KEY = 'alters_lab_onboarding_steps'

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

export default function GettingStarted({ onNavigate }: { onNavigate: (page: Page) => void }) {
  const { t } = useTranslation()
  const [completed, setCompleted] = useState<Set<number>>(loadCompleted)
  const [expanded, setExpanded] = useState<number | null>(1)
  const stepRefs = useRef<Map<number, HTMLDivElement>>(new Map())

  useEffect(() => {
    if (expanded !== null) {
      const el = stepRefs.current.get(expanded)
      if (el) expandIn(el)
    }
  }, [expanded])

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

  const steps = [
    {
      id: 1,
      title: t('gettingStarted.step1Title'),
      desc: t('gettingStarted.step1Desc'),
      action: t('gettingStarted.step1Action'),
      navigate: 'status' as Page,
    },
    {
      id: 2,
      title: t('gettingStarted.step2Title'),
      desc: t('gettingStarted.step2Desc'),
      action: t('gettingStarted.step2Action'),
      navigate: 'provider' as Page,
    },
    {
      id: 3,
      title: t('gettingStarted.step3Title'),
      desc: t('gettingStarted.step3Desc'),
      action: t('gettingStarted.step3Action'),
      navigate: 'weekly' as Page,
    },
    {
      id: 4,
      title: t('gettingStarted.step4Title'),
      desc: t('gettingStarted.step4Desc'),
      action: t('gettingStarted.step4Action'),
      navigate: null,
    },
  ]

  const doneCount = completed.size

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('gettingStarted.title')}</h2>

      <Card>
        <p className="text-sm mb-2" style={{ color: '#78716c' }}>
          {t('gettingStarted.progress')} {doneCount}/{steps.length}
        </p>
        <ProgressBar value={doneCount} max={steps.length} accent="amber" />
      </Card>

      {steps.map(step => (
        <div
          key={step.id}
          className="rounded-xl overflow-hidden transition-all duration-200"
          style={{
            backgroundColor: completed.has(step.id) ? '#f0fdf4' : '#ffffff',
            border: completed.has(step.id)
              ? '1px solid #bbf7d0'
              : expanded === step.id
                ? '1px solid #e8e6e1'
                : '1px solid #e8e6e1',
          }}
        >
          <button
            className="w-full px-4 py-3 flex items-center gap-3 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#b45309] focus-visible:ring-offset-2"
            style={{ backgroundColor: 'transparent' }}
            onClick={() => toggleStep(step.id)}
            aria-expanded={expanded === step.id}
            aria-controls={`step-content-${step.id}`}
          >
            <span
              className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0"
              style={{
                backgroundColor: completed.has(step.id) ? '#16a34a' : '#f5f4f0',
                color: completed.has(step.id) ? '#ffffff' : '#78716c',
              }}
            >
              {completed.has(step.id) ? '✓' : step.id}
            </span>
            <span className="text-sm font-medium flex-1" style={{ color: completed.has(step.id) ? '#16a34a' : '#1c1917' }}>
              {step.title}
            </span>
            <svg
              className="w-4 h-4 transition-transform duration-200 flex-shrink-0"
              style={{ color: '#a8a29e', transform: expanded === step.id ? 'rotate(180deg)' : 'rotate(0deg)' }}
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
            </svg>
          </button>

          {expanded === step.id && (
            <div ref={el => { if (el) stepRefs.current.set(step.id, el) }} id={`step-content-${step.id}`} role="region" className="px-4 pb-4 pt-1 space-y-3">
              <p className="text-sm leading-relaxed" style={{ color: '#78716c' }}>{step.desc}</p>
              <div className="flex gap-2">
                {step.navigate && (
                  <Button variant="secondary" onClick={() => onNavigate(step.navigate!)}>
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

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('gettingStarted.boundaries')}</h3>
        <p className="text-sm leading-relaxed" style={{ color: '#78716c' }}>
          <strong style={{ color: '#1c1917' }}>{t('gettingStarted.p6')}</strong> {t('gettingStarted.p6Desc')}<br />
          <strong style={{ color: '#1c1917' }}>{t('gettingStarted.p7')}</strong> {t('gettingStarted.p7Desc')}<br />
          <strong style={{ color: '#1c1917' }}>{t('gettingStarted.p8')}</strong> {t('gettingStarted.p8Desc')}<br />
          <strong style={{ color: '#1c1917' }}>{t('gettingStarted.providerOutput')}</strong> {t('gettingStarted.providerOutputDesc')}
        </p>
      </Card>
    </div>
  )
}
