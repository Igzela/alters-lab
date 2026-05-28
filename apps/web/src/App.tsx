import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { fadeIn } from './animations'
import { Button } from './components/Button'
import SystemStatus from './pages/SystemStatus'
import AlterDialogue from './pages/AlterDialogue'
import RealityScore from './pages/RealityScore'
import CalibrationHistory from './pages/CalibrationHistory'
import RubricDelta from './pages/RubricDelta'
import CheckpointPlan from './pages/CheckpointPlan'
import ProviderSettings from './pages/ProviderSettings'
import WeeklyReview from './pages/WeeklyReview'
import GettingStarted from './pages/GettingStarted'
import PatternReview from './pages/PatternReview'
import BehaviorValidation from './pages/BehaviorValidation'
import DataManagement from './pages/DataManagement'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started' | 'patterns' | 'validation' | 'data'

const navGroups: { pages: Page[]; accent: string }[] = [
  { pages: ['status', 'getting-started'], accent: 'green' },
  { pages: ['weekly', 'history', 'reality', 'rubric'], accent: 'lilac' },
  { pages: ['dialogue', 'provider'], accent: 'blue' },
  { pages: ['patterns', 'validation'], accent: 'orange' },
  { pages: ['checkpoint', 'data'], accent: 'green' },
]

export default function App() {
  const [page, setPage] = useState<Page>('status')
  const { t, i18n } = useTranslation()
  const pageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (pageRef.current) fadeIn(pageRef.current)
  }, [page])

  const toggleLang = () => {
    const next = i18n.language === 'en' ? 'zh' : 'en'
    i18n.changeLanguage(next)
    localStorage.setItem('alters_lab_language', next)
  }

  const navLabel: Record<Page, string> = {
    'status': t('nav.status'),
    'getting-started': t('nav.gettingStarted'),
    'weekly': t('nav.weeklyReview'),
    'dialogue': t('nav.dialogue'),
    'reality': t('nav.realityScore'),
    'history': t('nav.history'),
    'rubric': t('nav.rubricDelta'),
    'checkpoint': t('nav.checkpointPlan'),
    'provider': t('nav.provider'),
    'patterns': t('nav.patterns'),
    'validation': t('nav.validation'),
    'data': t('nav.data'),
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#0e100f', color: '#fffce1' }}>
      <div className="max-w-[960px] mx-auto px-6 py-8">
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>
            {t('app.title')}
          </h1>
          <Button variant="ghost" onClick={toggleLang}>
            {i18n.language === 'en' ? '中文' : 'EN'}
          </Button>
        </header>
        <nav className="flex gap-1 mb-8 flex-wrap items-center">
          {navGroups.map((group, gi) => (
            <div key={gi} className="flex gap-1">
              {gi > 0 && (
                <div className="w-px self-center mx-1" style={{ height: '1.25rem', backgroundColor: '#42433d' }} />
              )}
              {group.pages.map(p => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className="px-3 py-1.5 text-sm rounded-lg transition-all duration-200 border-none cursor-pointer"
                  style={{
                    backgroundColor: page === p ? '#242624' : 'transparent',
                    color: page === p ? '#fffce1' : '#7c7c6f',
                  }}
                  onMouseEnter={e => { if (page !== p) e.currentTarget.style.color = '#c4c2b8' }}
                  onMouseLeave={e => { if (page !== p) e.currentTarget.style.color = '#7c7c6f' }}
                >
                  {navLabel[p]}
                </button>
              ))}
            </div>
          ))}
        </nav>
        <div ref={pageRef}>
          {page === 'status' && <SystemStatus onNavigate={setPage} />}
          {page === 'weekly' && <WeeklyReview />}
          {page === 'dialogue' && <AlterDialogue />}
          {page === 'reality' && <RealityScore onNavigate={(p) => setPage(p as Page)} />}
          {page === 'history' && <CalibrationHistory />}
          {page === 'rubric' && <RubricDelta />}
          {page === 'checkpoint' && <CheckpointPlan />}
          {page === 'provider' && <ProviderSettings />}
          {page === 'getting-started' && <GettingStarted onNavigate={setPage} />}
          {page === 'patterns' && <PatternReview />}
          {page === 'validation' && <BehaviorValidation />}
          {page === 'data' && <DataManagement />}
        </div>
      </div>
    </div>
  )
}
