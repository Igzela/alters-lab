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
    <>
      <KeyboardShortcuts onNavigate={navigate} />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-3 focus:py-2 focus:rounded-lg focus:text-sm"
        style={{ backgroundColor: 'var(--color-text)', color: 'var(--color-bg)' }}
      >
        {t('common.skipToContent')}
      </a>

      {/* Desktop: sidebar layout */}
      <div className="hidden md:flex min-h-screen" style={{ backgroundColor: 'var(--color-bg)' }}>
        <Sidebar currentPage={currentPage} onNavigate={navigate} />
        <div className="flex-1 ml-[220px]">
          <div className="max-w-[1080px] mx-auto px-10 py-8">
            <main id="main-content" role="main">
              <PageRouter />
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
            <PageRouter />
          </main>
        </div>
        <MobileNav currentPage={currentPage} onNavigate={navigate} />
      </div>
    </>
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
