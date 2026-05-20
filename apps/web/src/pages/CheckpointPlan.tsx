import { useState } from 'react'
import { postJson } from '../api'

export default function CheckpointPlan() {
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await postJson('/checkpoint-regeneration/plan', { caller: 'api' })
      setData(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Checkpoint Plan</h2>
      <p style={{ color: '#888', fontSize: 12 }}>⚠ Plans are pending_review only. Cannot regenerate automatically.</p>
      <button onClick={generate} disabled={loading}>{loading ? '...' : 'Generate Plan'}</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {data && (
        <div style={{ marginTop: 12, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
          <p>Status: {String(data.status)}</p>
          {data.plan && <pre>{JSON.stringify(data.plan, null, 2)}</pre>}
        </div>
      )}
    </div>
  )
}
