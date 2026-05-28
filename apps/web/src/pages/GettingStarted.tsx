import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { expandIn, pulseSuccess } from '../animations'

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
  const contentRef = useRef<HTMLDivElement>(null)
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
      <h2 className="text-lg font-semibold">{t('gettingStarted.title')}</h2>

      <div className="p-3 bg-gray-800/50 rounded border border-gray-700">
        <p className="text-sm text-gray-300">
          {t('gettingStarted.progress')} {doneCount}/{steps.length}
        </p>
        <div className="mt-2 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 rounded-full transition-all duration-300"
            style={{ width: `${(doneCount / steps.length) * 100}%` }}
          />
        </div>
      </div>

      {steps.map(step => (
        <div
          key={step.id}
          className={`border rounded-lg overflow-hidden transition-colors ${
            completed.has(step.id)
              ? 'border-green-700 bg-green-900/10'
              : expanded === step.id
                ? 'border-gray-500 bg-gray-800/30'
                : 'border-gray-700 bg-gray-800/20'
          }`}
        >
          <button
            className="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-800/40 transition-colors"
            onClick={() => toggleStep(step.id)}
          >
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 ${
              completed.has(step.id)
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300'
            }`}>
              {completed.has(step.id) ? '✓' : step.id}
            </span>
            <span className={`text-sm font-medium ${completed.has(step.id) ? 'text-green-400' : 'text-white'}`}>
              {step.title}
            </span>
          </button>

          {expanded === step.id && (
            <div ref={el => { if (el) stepRefs.current.set(step.id, el) }} className="px-4 pb-4 pt-1 space-y-3">
              <p className="text-sm text-gray-400 leading-relaxed">{step.desc}</p>
              <div className="flex gap-2">
                {step.navigate && (
                  <button
                    className="px-3 py-1.5 text-xs bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
                    onClick={() => onNavigate(step.navigate!)}
                  >
                    {step.action}
                  </button>
                )}
                <button
                  className={`px-3 py-1.5 text-xs rounded transition-colors ${
                    completed.has(step.id)
                      ? 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                      : 'bg-green-700 text-white hover:bg-green-600'
                  }`}
                  onClick={(e) => {
                    markComplete(step.id)
                    if (!completed.has(step.id)) pulseSuccess(e.currentTarget)
                  }}
                >
                  {completed.has(step.id) ? t('gettingStarted.markIncomplete') : t('gettingStarted.markComplete')}
                </button>
              </div>
            </div>
          )}
        </div>
      ))}

      <div className="mb-6 p-4 border border-gray-600 rounded-lg">
        <h3 className="text-sm font-medium mb-2">{t('gettingStarted.boundaries')}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">
          <strong>{t('gettingStarted.p6')}</strong> {t('gettingStarted.p6Desc')}<br />
          <strong>{t('gettingStarted.p7')}</strong> {t('gettingStarted.p7Desc')}<br />
          <strong>{t('gettingStarted.p8')}</strong> {t('gettingStarted.p8Desc')}<br />
          <strong>{t('gettingStarted.providerOutput')}</strong> {t('gettingStarted.providerOutputDesc')}
        </p>
      </div>
    </div>
  )
}
