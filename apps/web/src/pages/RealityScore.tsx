import { useState } from 'react'
import { postJson } from '../api'

const ALTERS = [
  { alter: 'alter_A', branch: 'branch_A' },
  { alter: 'alter_B', branch: 'branch_B' },
  { alter: 'alter_C', branch: 'branch_C' },
  { alter: 'alter_D', branch: 'branch_D' },
]

const DIMS = ['execution_discipline', 'exploration_freedom', 'life_state_match', 'energy_level'] as const

export default function RealityScore() {
  const [pair, setPair] = useState(0)
  const [scores, setScores] = useState<Record<string, number>>({
    execution_discipline: 3,
    exploration_freedom: 3,
    life_state_match: 3,
    energy_level: 3,
  })
  const [notes, setNotes] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  const submit = async () => {
    setError('')
    setStatus('')
    try {
      const res = await postJson('/calibration-loop/reality-scores', {
        score_id: `score_manual_${Date.now()}`,
        branch_id: ALTERS[pair].branch,
        alter_id: ALTERS[pair].alter,
        actual_scores: scores,
        user_notes: notes,
        submitted_by_user: true,
        source: 'explicit_user_submission',
        caller: 'api',
      })
      setStatus(`Score recorded: ${res.record.id}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    }
  }

  return (
    <div>
      <h2>Reality Score</h2>
      <p style={{ color: '#888', fontSize: 12 }}>Scores require explicit user submission. No auto-inference from dialogue.</p>
      <select value={pair} onChange={e => setPair(Number(e.target.value))} style={{ marginBottom: 12 }}>
        {ALTERS.map((a, i) => <option key={a.alter} value={i}>{a.alter} / {a.branch}</option>)}
      </select>
      {DIMS.map(d => (
        <div key={d} style={{ marginBottom: 8 }}>
          <label>{d}: </label>
          <input type="range" min={1} max={5} value={scores[d]}
            onChange={e => setScores({ ...scores, [d]: Number(e.target.value) })} />
          <span>{scores[d]}</span>
        </div>
      ))}
      <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Notes..." style={{ width: '100%', minHeight: 60 }} />
      <button onClick={submit} style={{ marginTop: 8 }}>Submit Score</button>
      {status && <p style={{ color: 'green' }}>{status}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  )
}
