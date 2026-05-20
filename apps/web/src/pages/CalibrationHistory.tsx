import { useState, useEffect } from 'react'
import { fetchJson } from '../api'

export default function CalibrationHistory() {
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchJson('/calibration-loop/history')
      .then(setData)
      .catch(e => setError(e.message))
  }, [])

  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>
  if (!data) return <p>Loading...</p>

  const records = (data.records as Record<string, unknown>[]) || []
  const drift = (data.drift_evidence as Record<string, unknown>[]) || []

  return (
    <div>
      <h2>Calibration History</h2>
      <p>Read-only: {data.read_only ? 'Yes' : 'No'}</p>
      <h3>Scores ({data.count})</h3>
      {records.length === 0 && <p>No scores yet.</p>}
      {records.map(r => (
        <div key={String(r.id)} style={{ padding: 8, marginBottom: 8, background: '#f9f9f9' }}>
          <strong>{String(r.id)}</strong> — {String(r.alter_id)}<br />
          Actual: {JSON.stringify(r.actual_scores)}
        </div>
      ))}
      {drift.length > 0 && (
        <>
          <h3>Drift Evidence</h3>
          {drift.map((d, i) => (
            <div key={i} style={{ padding: 8, marginBottom: 8, background: '#fff3f3' }}>
              Overall: {String(d.overall)} | Threshold exceeded: {String(d.threshold_exceeded)}
            </div>
          ))}
        </>
      )}
    </div>
  )
}
