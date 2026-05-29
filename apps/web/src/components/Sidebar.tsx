import { useTranslation } from 'react-i18next'
import {
  House,
  Compass,
  ClipboardText,
  ChatCircle,
  ChartLineUp,
  GitBranch,
  Gear,
  MagnifyingGlass,
  ArrowsClockwise,
  Database,
  Sparkle,
  ShieldCheck,
} from '@phosphor-icons/react'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started' | 'patterns' | 'validation' | 'data'

interface NavItem {
  page: Page
  icon: React.ReactNode
  labelKey: string
}

interface NavGroup {
  labelKey: string
  items: NavItem[]
}

const navGroups: NavGroup[] = [
  {
    labelKey: 'nav.overview',
    items: [
      { page: 'status', icon: <House size={18} />, labelKey: 'nav.status' },
      { page: 'getting-started', icon: <Compass size={18} />, labelKey: 'nav.gettingStarted' },
    ],
  },
  {
    labelKey: 'nav.calibration',
    items: [
      { page: 'weekly', icon: <ClipboardText size={18} />, labelKey: 'nav.weeklyReview' },
      { page: 'history', icon: <ChartLineUp size={18} />, labelKey: 'nav.history' },
      { page: 'reality', icon: <Sparkle size={18} />, labelKey: 'nav.realityScore' },
      { page: 'rubric', icon: <ArrowsClockwise size={18} />, labelKey: 'nav.rubricDelta' },
    ],
  },
  {
    labelKey: 'nav.dialogue',
    items: [
      { page: 'dialogue', icon: <ChatCircle size={18} />, labelKey: 'nav.dialogue' },
      { page: 'provider', icon: <Gear size={18} />, labelKey: 'nav.provider' },
    ],
  },
  {
    labelKey: 'nav.analysis',
    items: [
      { page: 'patterns', icon: <MagnifyingGlass size={18} />, labelKey: 'nav.patterns' },
      { page: 'validation', icon: <ShieldCheck size={18} />, labelKey: 'nav.validation' },
    ],
  },
  {
    labelKey: 'nav.system',
    items: [
      { page: 'checkpoint', icon: <GitBranch size={18} />, labelKey: 'nav.checkpointPlan' },
      { page: 'data', icon: <Database size={18} />, labelKey: 'nav.data' },
    ],
  },
]

interface SidebarProps {
  currentPage: Page
  onNavigate: (page: Page) => void
}

export default function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  const { t, i18n } = useTranslation()

  const toggleLang = () => {
    const next = i18n.language === 'en' ? 'zh' : 'en'
    i18n.changeLanguage(next)
    localStorage.setItem('alters_lab_language', next)
  }

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-[220px] flex flex-col z-30" style={{ backgroundColor: '#1c1917' }}>
      <div className="px-5 pt-6 pb-4">
        <h1 className="text-base font-semibold tracking-tight" style={{ color: '#faf9f7' }}>
          {t('app.title')}
        </h1>
      </div>

      <nav className="flex-1 overflow-y-auto px-3" role="navigation" aria-label={t('app.title')}>
        {navGroups.map((group, gi) => (
          <div key={gi} className="mb-4">
            <div className="px-2 mb-1 text-[11px] font-medium uppercase tracking-wider" style={{ color: '#78716c' }}>
              {t(group.labelKey)}
            </div>
            {group.items.map(item => {
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
            })}
          </div>
        ))}
      </nav>

      <div className="px-3 py-4 border-t" style={{ borderColor: '#292524' }}>
        <button
          onClick={toggleLang}
          className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-sm transition-colors duration-150 border-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#b45309]"
          style={{ color: '#78716c', backgroundColor: 'transparent' }}
          onMouseEnter={e => { e.currentTarget.style.backgroundColor = '#292524'; e.currentTarget.style.color = '#d6d3d1' }}
          onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#78716c' }}
          aria-label={i18n.language === 'en' ? 'Switch to Chinese' : 'Switch to English'}
        >
          <span className="text-xs">{i18n.language === 'en' ? 'EN' : 'ZH'}</span>
          <span className="text-xs">{i18n.language === 'en' ? '中文' : 'English'}</span>
        </button>
      </div>
    </aside>
  )
}
