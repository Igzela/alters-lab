import { useState } from 'react'
import SystemStatus from './pages/SystemStatus'
import AlterDialogue from './pages/AlterDialogue'
import RealityScore from './pages/RealityScore'
import CalibrationHistory from './pages/CalibrationHistory'
import RubricDelta from './pages/RubricDelta'
import CheckpointPlan from './pages/CheckpointPlan'
import ProviderSettings from './pages/ProviderSettings'

type Page = 'status' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider'

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
        <button style={navStyle('dialogue')} onClick={() => setPage('dialogue')}>Dialogue</button>
        <button style={navStyle('reality')} onClick={() => setPage('reality')}>Reality Score</button>
        <button style={navStyle('history')} onClick={() => setPage('history')}>History</button>
        <button style={navStyle('rubric')} onClick={() => setPage('rubric')}>Rubric Delta</button>
        <button style={navStyle('checkpoint')} onClick={() => setPage('checkpoint')}>Checkpoint Plan</button>
        <button style={navStyle('provider')} onClick={() => setPage('provider')}>Provider</button>
      </nav>
      {page === 'status' && <SystemStatus />}
      {page === 'dialogue' && <AlterDialogue />}
      {page === 'reality' && <RealityScore />}
      {page === 'history' && <CalibrationHistory />}
      {page === 'rubric' && <RubricDelta />}
      {page === 'checkpoint' && <CheckpointPlan />}
      {page === 'provider' && <ProviderSettings />}
    </div>
  )
}
