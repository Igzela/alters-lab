import { BrowserRouter } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Sun, Moon } from '@phosphor-icons/react'
import { ToastProvider } from './components/Toast'
import { useTheme } from './components/ThemeContext'
import { NavigationProvider, useNavigation } from './components/NavigationContext'
import KeyboardShortcuts from './components/KeyboardShortcuts'
import ErrorBoundary from './components/ErrorBoundary'
import Sidebar from './components/Sidebar'
import MobileNav from './components/MobileNav'
import PageRouter from './components/PageRouter'

function AppLayout() {
  const { t } = useTranslation()
  const { theme, toggleTheme } = useTheme()
  const { currentPage, navigate } = useNavigation()

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-bg)' }}>
      <KeyboardShortcuts onNavigate={navigate} />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-3 focus:py-2 focus:rounded-lg focus:text-sm"
        style={{ backgroundColor: 'var(--color-text)', color: 'var(--color-bg)' }}
      >
        {t('common.skipToContent')}
      </a>

      {/* Desktop sidebar — hidden on mobile */}
      <div className="hidden md:block">
        <Sidebar currentPage={currentPage} onNavigate={navigate} />
      </div>

      {/* Mobile header — hidden on desktop */}
      <div className="md:hidden px-4 pt-6">
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
      </div>

      {/* Shared main content — rendered once, visible in both layouts */}
      <div className="md:ml-[220px] pb-16 md:pb-0">
        <div className="max-w-[1080px] mx-auto px-4 md:px-10 py-6 md:py-8">
          <main id="main-content" role="main">
            <PageRouter />
          </main>
        </div>
      </div>

      {/* Mobile bottom nav — hidden on desktop */}
      <div className="md:hidden">
        <MobileNav currentPage={currentPage} onNavigate={navigate} />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ToastProvider>
          <NavigationProvider>
            <AppLayout />
          </NavigationProvider>
        </ToastProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
