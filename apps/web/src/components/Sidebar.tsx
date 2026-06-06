import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { STORAGE_KEY as LANG_STORAGE_KEY } from '../i18n'
import {
  ClipboardText,
  ChatCircle,
  ChartLineUp,
  Gear,
  MagnifyingGlass,
  ArrowsClockwise,
  Database,
  Sparkle,
  ShieldCheck,
  Sun,
  Moon,
  ChartBarIcon,
  TrendUp,
  Binoculars,
  Target,
  Books,
  Pulse,
  Gauge,
  CaretDown,
  CaretRight,
} from '@phosphor-icons/react'
import type { Page } from '../types'
import { useTheme } from './ThemeContext'

interface SidebarProps {
  currentPage: Page
  onNavigate: (page: Page) => void
}

const coreItems: { page: Page; icon: React.ReactNode; labelKey: string }[] = [
  { page: 'dashboard', icon: <ChartBarIcon size={18} />, labelKey: 'nav.home' },
  { page: 'p6-progress', icon: <TrendUp size={18} />, labelKey: 'nav.yourProgress' },
  { page: 'dialogue', icon: <ChatCircle size={18} />, labelKey: 'nav.dialogue' },
  { page: 'weekly', icon: <ClipboardText size={18} />, labelKey: 'nav.weeklyReview' },
  { page: 'branch-forecast', icon: <Binoculars size={18} />, labelKey: 'nav.branchForecast' },
  { page: 'outcome-targets', icon: <Target size={18} />, labelKey: 'nav.outcomeTargets' },
  { page: 'forecast-calibration', icon: <ChartLineUp size={18} />, labelKey: 'nav.forecastCalibration' },
]

const moreItems: { page: Page; icon: React.ReactNode; labelKey: string }[] = [
  { page: 'calibration-conversation', icon: <ChatCircle size={18} />, labelKey: 'nav.calibrationConversation' },
  { page: 'behavior-metrics', icon: <Pulse size={18} />, labelKey: 'nav.behaviorMetrics' },
  { page: 'reality', icon: <Sparkle size={18} />, labelKey: 'nav.realityScore' },
  { page: 'rubric', icon: <ArrowsClockwise size={18} />, labelKey: 'nav.rubricDelta' },
  { page: 'patterns', icon: <MagnifyingGlass size={18} />, labelKey: 'nav.patterns' },
  { page: 'validation', icon: <ShieldCheck size={18} />, labelKey: 'nav.validation' },
  { page: 'public-priors', icon: <Books size={18} />, labelKey: 'nav.publicPriors' },
  { page: 'strength-overview', icon: <Gauge size={18} />, labelKey: 'nav.strengthOverview' },
  { page: 'predictor-profile', icon: <TrendUp size={18} />, labelKey: 'nav.predictorProfile' },
  { page: 'provider', icon: <Gear size={18} />, labelKey: 'nav.provider' },
  { page: 'data', icon: <Database size={18} />, labelKey: 'nav.data' },
]

export default function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  const { t, i18n } = useTranslation()
  const { theme, toggleTheme } = useTheme()
  const [moreOpen, setMoreOpen] = useState(false)

  const toggleLang = () => {
    const next = i18n.language === 'en' ? 'zh' : 'en'
    i18n.changeLanguage(next)
    localStorage.setItem(LANG_STORAGE_KEY, next)
  }

  const renderItem = (item: { page: Page; icon: React.ReactNode; labelKey: string }) => {
    const isActive = currentPage === item.page
    return (
      <button
        key={item.page}
        onClick={() => onNavigate(item.page)}
        aria-current={isActive ? 'page' : undefined}
        className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-sm transition-colors duration-150 border-none cursor-pointer text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#b45309] focus-visible:ring-offset-1 focus-visible:ring-offset-[#1c1917]"
        style={{
          backgroundColor: isActive ? '#44403c' : 'transparent',
          color: isActive ? '#faf9f7' : '#a8a29e',
          borderLeft: isActive ? '2px solid #b45309' : '2px solid transparent',
        }}
        onMouseEnter={e => { if (!isActive) { e.currentTarget.style.backgroundColor = '#292524'; e.currentTarget.style.color = '#d6d3d1' } }}
        onMouseLeave={e => { if (!isActive) { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#a8a29e' } }}
      >
        <span className="flex-shrink-0">{item.icon}</span>
        <span>{t(item.labelKey)}</span>
      </button>
    )
  }

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-[220px] flex flex-col z-30" style={{ backgroundColor: '#1c1917' }}>
      <div className="px-5 pt-6 pb-4">
        <h1 className="text-base font-semibold tracking-tight" style={{ color: '#faf9f7' }}>
          {t('app.title')}
        </h1>
      </div>

      <nav className="flex-1 overflow-y-auto px-3" role="navigation" aria-label={t('app.title')}>
        <div className="mb-4">
          {coreItems.map(renderItem)}
        </div>

        <div className="mb-4">
          <button
            onClick={() => setMoreOpen(v => !v)}
            className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-sm border-none cursor-pointer text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#b45309]"
            style={{ color: '#78716c', backgroundColor: 'transparent' }}
            onMouseEnter={e => { e.currentTarget.style.backgroundColor = '#292524'; e.currentTarget.style.color = '#d6d3d1' }}
            onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#78716c' }}
            aria-expanded={moreOpen}
          >
            {moreOpen ? <CaretDown size={14} /> : <CaretRight size={14} />}
            <span>{t('nav.more')}</span>
          </button>
          {moreOpen && moreItems.map(renderItem)}
        </div>
      </nav>

      <div className="px-3 py-4 border-t" style={{ borderColor: '#292524' }}>
        <div className="flex gap-1">
          <button
            onClick={toggleTheme}
            className="flex-1 flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg text-sm transition-colors duration-150 border-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#b45309]"
            style={{ color: '#78716c', backgroundColor: 'transparent' }}
            onMouseEnter={e => { e.currentTarget.style.backgroundColor = '#292524'; e.currentTarget.style.color = '#d6d3d1' }}
            onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#78716c' }}
            aria-label={theme === 'light' ? t('nav.switchToDark') : t('nav.switchToLight')}
          >
            {theme === 'light' ? <Moon size={14} /> : <Sun size={14} />}
            <span className="text-xs">{theme === 'light' ? t('nav.themeDark') : t('nav.themeLight')}</span>
          </button>
          <button
            onClick={toggleLang}
            className="flex-1 flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg text-sm transition-colors duration-150 border-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#b45309]"
            style={{ color: '#78716c', backgroundColor: 'transparent' }}
            onMouseEnter={e => { e.currentTarget.style.backgroundColor = '#292524'; e.currentTarget.style.color = '#d6d3d1' }}
            onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#78716c' }}
            aria-label={i18n.language === 'en' ? t('nav.switchToChinese') : t('nav.switchToEnglish')}
          >
            <span className="text-xs">{i18n.language === 'en' ? 'EN' : 'ZH'}</span>
          </button>
        </div>
      </div>
    </aside>
  )
}
