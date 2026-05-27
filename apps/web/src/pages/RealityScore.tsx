import { useState, useEffect } from 'react'
import { postJson, listActionAlignmentScores } from '../api'
import type { ActionAlignmentScore } from '../types'

const ALTERS = [
  { alter: 'alter_A', branch: 'branch_A' },
  { alter: 'alter_B', branch: 'branch_B' },
  { alter: 'alter_C', branch: 'branch_C' },
  { alter: 'alter_D', branch: 'branch_D' },
]

const DIMS = ['execution_discipline', 'exploration_freedom', 'life_state_match', 'energy_level'] as const

export default function RealityScore({ onNavigate }: { onNavigate?: (page: string) => void }) {
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
  const [recentScores, setRecentScores] = useState<ActionAlignmentScore[]>([])

  useEffect(() => {
    listActionAlignmentScores()
      .then(res => {
        const sorted = [...res.scores].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        setRecentScores(sorted.slice(0, 5))
      })
      .catch(() => {})
  }, [])

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
      <p style={{ padding: 10, background: '#fff7ed', border: '1px solid #fed7aa' }}>
        This page is for manual score submission. For real weekly review, use Weekly Review.
      </p>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {onNavigate && <button onClick={() => onNavigate('weekly')}>Go to Weekly Review</button>}
        {onNavigate && <a href="#history" onClick={e => { e.preventDefault(); onNavigate('history') }}>View Calibration History</a>}
      </div>

      {recentScores.length > 0 && (
        <div style={{ marginBottom: 16, padding: 12, background: '#f6f8ff', borderRadius: 6, border: '1px solid #d0daf0' }}>
          <h4 style={{ margin: '0 0 8px' }}>Recent Action Alignment Scores</h4>
          <p style={{ margin: '0 0 8px', fontSize: 13, color: '#666' }}>
            These scores come from your weekly reviews. Manual reality scores (submitted here) are separate calibration inputs.
          </p>
          {recentScores.map(s => (
            <div key={s.score_id} style={{ padding: 6, marginBottom: 4, background: '#fff', borderRadius: 4 }}>
              <strong>{s.action_alignment_score.toFixed(2)}</strong> — {s.verdict_label.replace(/_/g, ' ')}
              {s.created_at && <span style={{ fontSize: 12, color: '#888', marginLeft: 8 }}>{s.created_at}</span>}
            </div>
          ))}
        </div>
      )}

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
