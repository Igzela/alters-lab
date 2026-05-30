import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Sun, Moon } from '@phosphor-icons/react'
import { fadeIn } from './animations'
import { ToastProvider } from './components/Toast'
import { useTheme } from './components/ThemeContext'
import KeyboardShortcuts from './components/KeyboardShortcuts'
import ErrorBoundary from './components/ErrorBoundary'
import Sidebar from './components/Sidebar'
import MobileNav from './components/MobileNav'
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
import Dashboard from './pages/Dashboard'
import type { Page } from './types'
import { VALID_PAGES } from './types'

function getPageFromHash(): Page {
  const hash = window.location.hash.replace('#', '')
  if (VALID_PAGES.includes(hash as Page)) return hash as Page
  return 'dashboard'
}

export default function App() {
  const [page, setPage] = useState<Page>(getPageFromHash)
  const { t } = useTranslation()
  const { theme, toggleTheme } = useTheme()
  const pageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (pageRef.current) fadeIn(pageRef.current)
    window.location.hash = page
  }, [page])

  useEffect(() => {
    const onHashChange = () => {
      const p = getPageFromHash()
      if (VALID_PAGES.includes(p)) setPage(p)
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const handleNavigate = (p: Page) => setPage(p)

  return (
    <ErrorBoundary>
    <ToastProvider>
      <KeyboardShortcuts onNavigate={handleNavigate} />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-3 focus:py-2 focus:rounded-lg focus:text-sm"
        style={{ backgroundColor: 'var(--color-text)', color: 'var(--color-bg)' }}
      >
        {t('common.skipToContent')}
      </a>

      {/* Desktop: sidebar layout */}
      <div className="hidden md:flex min-h-screen" style={{ backgroundColor: 'var(--color-bg)' }}>
        <Sidebar currentPage={page} onNavigate={handleNavigate} />
        <div className="flex-1 ml-[220px]">
          <div className="max-w-[1080px] mx-auto px-10 py-8">
            <main ref={pageRef} id="main-content" role="main">
              {page === 'dashboard' && <Dashboard />}
              {page === 'status' && <SystemStatus onNavigate={handleNavigate} />}
              {page === 'weekly' && <WeeklyReview />}
              {page === 'dialogue' && <AlterDialogue />}
              {page === 'reality' && <RealityScore onNavigate={(p) => handleNavigate(p as Page)} />}
              {page === 'history' && <CalibrationHistory />}
              {page === 'rubric' && <RubricDelta />}
              {page === 'checkpoint' && <CheckpointPlan />}
              {page === 'provider' && <ProviderSettings />}
              {page === 'getting-started' && <GettingStarted onNavigate={handleNavigate} />}
              {page === 'patterns' && <PatternReview />}
              {page === 'validation' && <BehaviorValidation />}
              {page === 'data' && <DataManagement />}
            </main>
          </div>
        </div>
      </div>

      {/* Mobile: bottom nav layout */}
      <div className="md:hidden min-h-screen pb-16" style={{ backgroundColor: 'var(--color-bg)' }}>
        <div className="px-4 py-6">
          <header className="flex justify-between items-center mb-6">
            <h1 className="text-lg font-semibold tracking-tight" style={{ color: 'var(--color-text)' }}>
              {t('app.title')}
            </h1>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg transition-colors duration-150 border-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]"
              style={{ color: 'var(--color-text-secondary)', backgroundColor: 'transparent' }}
              aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>
          </header>
          <main id="main-content" role="main">
            {page === 'dashboard' && <Dashboard />}
            {page === 'status' && <SystemStatus onNavigate={handleNavigate} />}
            {page === 'weekly' && <WeeklyReview />}
            {page === 'dialogue' && <AlterDialogue />}
            {page === 'reality' && <RealityScore onNavigate={(p) => handleNavigate(p as Page)} />}
            {page === 'history' && <CalibrationHistory />}
            {page === 'rubric' && <RubricDelta />}
            {page === 'checkpoint' && <CheckpointPlan />}
            {page === 'provider' && <ProviderSettings />}
            {page === 'getting-started' && <GettingStarted onNavigate={handleNavigate} />}
            {page === 'patterns' && <PatternReview />}
            {page === 'validation' && <BehaviorValidation />}
            {page === 'data' && <DataManagement />}
          </main>
        </div>
        <MobileNav currentPage={page} onNavigate={handleNavigate} />
      </div>
    </ToastProvider>
    </ErrorBoundary>
  )
}
