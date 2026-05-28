import { useState } from 'react'
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

  const navBtn = (p: Page) =>
    `px-4 py-2 text-sm rounded-md transition-colors ${
      page === p
        ? 'bg-gray-800 text-white'
        : 'bg-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
    }`

  return (
    <div className="font-sans max-w-[900px] mx-auto p-5">
      <h1 className="text-xl font-semibold mb-4">Alters Lab</h1>
      <nav className="flex gap-1 mb-5 flex-wrap">
        <button className={navBtn('status')} onClick={() => setPage('status')}>Status</button>
        <button className={navBtn('getting-started')} onClick={() => setPage('getting-started')}>Getting Started</button>
        <button className={navBtn('weekly')} onClick={() => setPage('weekly')}>Weekly Review</button>
        <button className={navBtn('dialogue')} onClick={() => setPage('dialogue')}>Dialogue</button>
        <button className={navBtn('reality')} onClick={() => setPage('reality')}>Reality Score</button>
        <button className={navBtn('history')} onClick={() => setPage('history')}>History</button>
        <button className={navBtn('rubric')} onClick={() => setPage('rubric')}>Rubric Delta</button>
        <button className={navBtn('checkpoint')} onClick={() => setPage('checkpoint')}>Checkpoint Plan</button>
        <button className={navBtn('provider')} onClick={() => setPage('provider')}>Provider</button>
        <button className={navBtn('patterns')} onClick={() => setPage('patterns')}>Patterns</button>
        <button className={navBtn('validation')} onClick={() => setPage('validation')}>Validation</button>
        <button className={navBtn('data')} onClick={() => setPage('data')}>Data</button>
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
