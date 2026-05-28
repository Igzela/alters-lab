import { useState } from 'react'
import { useTranslation } from 'react-i18next'
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

export default function App() {
  const [page, setPage] = useState<Page>('status')
  const { t, i18n } = useTranslation()

  const toggleLang = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'zh' : 'en')
  }

  const navBtn = (p: Page) =>
    `px-4 py-2 text-sm rounded-md transition-colors ${
      page === p
        ? 'bg-gray-800 text-white'
        : 'bg-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
    }`

  return (
    <div className="font-sans max-w-[900px] mx-auto p-5">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-semibold">{t('app.title')}</h1>
        <button
          onClick={toggleLang}
          className="px-3 py-1.5 text-xs bg-gray-800 text-gray-300 rounded border border-gray-700 hover:bg-gray-700 hover:text-white transition-colors"
        >
          {i18n.language === 'en' ? '中文' : 'EN'}
        </button>
      </div>
      <nav className="flex gap-1 mb-5 flex-wrap">
        <button className={navBtn('status')} onClick={() => setPage('status')}>{t('nav.status')}</button>
        <button className={navBtn('getting-started')} onClick={() => setPage('getting-started')}>{t('nav.gettingStarted')}</button>
        <button className={navBtn('weekly')} onClick={() => setPage('weekly')}>{t('nav.weeklyReview')}</button>
        <button className={navBtn('dialogue')} onClick={() => setPage('dialogue')}>{t('nav.dialogue')}</button>
        <button className={navBtn('reality')} onClick={() => setPage('reality')}>{t('nav.realityScore')}</button>
        <button className={navBtn('history')} onClick={() => setPage('history')}>{t('nav.history')}</button>
        <button className={navBtn('rubric')} onClick={() => setPage('rubric')}>{t('nav.rubricDelta')}</button>
        <button className={navBtn('checkpoint')} onClick={() => setPage('checkpoint')}>{t('nav.checkpointPlan')}</button>
        <button className={navBtn('provider')} onClick={() => setPage('provider')}>{t('nav.provider')}</button>
        <button className={navBtn('patterns')} onClick={() => setPage('patterns')}>{t('nav.patterns')}</button>
        <button className={navBtn('validation')} onClick={() => setPage('validation')}>{t('nav.validation')}</button>
        <button className={navBtn('data')} onClick={() => setPage('data')}>{t('nav.data')}</button>
      </nav>
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
  )
}
