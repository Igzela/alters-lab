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
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Reality Score</h2>
      <p className="text-gray-500 text-xs">Scores require explicit user submission. No auto-inference from dialogue.</p>
      <p className="p-2.5 bg-amber-950/30 border border-amber-800/50 rounded text-sm text-amber-200">
        This page is for manual score submission. For real weekly review, use Weekly Review.
      </p>
      <div className="flex gap-2">
        {onNavigate && (
          <button className="px-3 py-1.5 text-sm bg-gray-800 text-white rounded hover:bg-gray-700" onClick={() => onNavigate('weekly')}>
            Go to Weekly Review
          </button>
        )}
        {onNavigate && (
          <button className="px-3 py-1.5 text-sm text-blue-400 hover:text-blue-300" onClick={() => onNavigate('history')}>
            View Calibration History
          </button>
        )}
      </div>

      {recentScores.length > 0 && (
        <div className="mb-4 p-3 bg-blue-950/30 rounded-lg border border-blue-800/30">
          <h4 className="text-sm font-medium mb-2">Recent Action Alignment Scores</h4>
          <p className="text-xs text-gray-400 mb-2">
            These scores come from your weekly reviews. Manual reality scores (submitted here) are separate calibration inputs.
          </p>
          {recentScores.map(s => (
            <div key={s.score_id} className="py-1 text-sm">
              <strong>{s.action_alignment_score.toFixed(2)}</strong> — {s.verdict_label.replace(/_/g, ' ')}
              {s.created_at && <span className="text-xs text-gray-500 ml-2">{s.created_at}</span>}
            </div>
          ))}
        </div>
      )}

      <select
        className="border border-gray-600 rounded px-3 py-2 text-sm bg-gray-800 text-white mb-3"
        value={pair}
        onChange={e => setPair(Number(e.target.value))}
      >
        {ALTERS.map((a, i) => <option key={a.alter} value={i}>{a.alter} / {a.branch}</option>)}
      </select>
      {DIMS.map(d => (
        <div key={d} className="flex items-center gap-2 text-sm">
          <label className="w-40 text-gray-300">{d}</label>
          <input type="range" min={1} max={5} value={scores[d]}
            onChange={e => setScores({ ...scores, [d]: Number(e.target.value) })} className="flex-1" />
          <span className="w-6 text-center">{scores[d]}</span>
        </div>
      ))}
      <textarea
        className="w-full border border-gray-600 rounded px-3 py-2 text-sm bg-gray-800 text-white placeholder-gray-500 min-h-[60px]"
        value={notes}
        onChange={e => setNotes(e.target.value)}
        placeholder="Notes..."
      />
      <button
        className="mt-2 px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700"
        onClick={submit}
      >
        Submit Score
      </button>
      {status && <p className="text-green-400 text-sm">{status}</p>}
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  )
}
