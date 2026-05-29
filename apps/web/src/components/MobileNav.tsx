import { useTranslation } from 'react-i18next'
import {
  House,
  ClipboardText,
  ChatCircle,
  MagnifyingGlass,
  Gear,
} from '@phosphor-icons/react'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started' | 'patterns' | 'validation' | 'data'

interface MobileNavProps {
  currentPage: Page
  onNavigate: (page: Page) => void
}

const tabs: { page: Page; icon: React.ReactNode; labelKey: string }[] = [
  { page: 'status', icon: <House size={20} />, labelKey: 'nav.status' },
  { page: 'weekly', icon: <ClipboardText size={20} />, labelKey: 'nav.weeklyReview' },
  { page: 'dialogue', icon: <ChatCircle size={20} />, labelKey: 'nav.dialogue' },
  { page: 'patterns', icon: <MagnifyingGlass size={20} />, labelKey: 'nav.patterns' },
  { page: 'provider', icon: <Gear size={20} />, labelKey: 'nav.provider' },
]

export default function MobileNav({ currentPage, onNavigate }: MobileNavProps) {
  const { t } = useTranslation()

  const isActive = (page: Page) => {
    if (page === 'status') return currentPage === 'status' || currentPage === 'getting-started'
    if (page === 'weekly') return ['weekly', 'history', 'reality', 'rubric'].includes(currentPage)
    if (page === 'dialogue') return currentPage === 'dialogue'
    if (page === 'patterns') return ['patterns', 'validation'].includes(currentPage)
    if (page === 'provider') return ['provider', 'checkpoint', 'data'].includes(currentPage)
    return false
  }

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around border-t safe-area-pb"
      style={{ backgroundColor: '#ffffff', borderColor: '#e8e6e1', paddingBottom: 'env(safe-area-inset-bottom)' }}
      role="navigation"
      aria-label={t('app.title')}
    >
      {tabs.map(tab => {
        const active = isActive(tab.page)
        return (
          <button
            key={tab.page}
            onClick={() => onNavigate(tab.page)}
            aria-current={active ? 'page' : undefined}
            className="flex flex-col items-center gap-0.5 py-2 px-3 border-none cursor-pointer transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#b45309]"
            style={{
              backgroundColor: 'transparent',
              color: active ? '#b45309' : '#a8a29e',
            }}
          >
            {tab.icon}
            <span className="text-[10px] font-medium">{t(tab.labelKey)}</span>
          </button>
        )
      })}
    </nav>
  )
}
