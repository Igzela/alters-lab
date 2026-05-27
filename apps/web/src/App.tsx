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

  const navStyle = (p: Page) => ({
    padding: '8px 16px',
    cursor: 'pointer',
    background: page === p ? '#333' : 'transparent',
    color: page === p ? '#fff' : '#aaa',
    border: 'none',
    fontSize: '14px',
  })

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: 900, margin: '0 auto', padding: 20 }}>
      <h1 style={{ fontSize: 20, marginBottom: 16 }}>Alters Lab — Local MVP</h1>
      <nav style={{ display: 'flex', gap: 4, marginBottom: 20, flexWrap: 'wrap' }}>
        <button style={navStyle('status')} onClick={() => setPage('status')}>Status</button>
        <button style={navStyle('getting-started')} onClick={() => setPage('getting-started')}>Getting Started</button>
        <button style={navStyle('weekly')} onClick={() => setPage('weekly')}>Weekly Review</button>
        <button style={navStyle('dialogue')} onClick={() => setPage('dialogue')}>Dialogue</button>
        <button style={navStyle('reality')} onClick={() => setPage('reality')}>Reality Score</button>
        <button style={navStyle('history')} onClick={() => setPage('history')}>History</button>
        <button style={navStyle('rubric')} onClick={() => setPage('rubric')}>Rubric Delta</button>
        <button style={navStyle('checkpoint')} onClick={() => setPage('checkpoint')}>Checkpoint Plan</button>
        <button style={navStyle('provider')} onClick={() => setPage('provider')}>Provider</button>
        <button style={navStyle('patterns')} onClick={() => setPage('patterns')}>Patterns</button>
        <button style={navStyle('validation')} onClick={() => setPage('validation')}>Validation</button>
        <button style={navStyle('data')} onClick={() => setPage('data')}>Data</button>
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
