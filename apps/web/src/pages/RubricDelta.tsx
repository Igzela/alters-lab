import { useState } from 'react'
import { postJson } from '../api'

export default function RubricDelta() {
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await postJson('/rubric-delta/suggest', { caller: 'api' })
      setData(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Rubric Delta</h2>
      <p style={{ color: '#888', fontSize: 12 }}>⚠ Suggestions are pending_review only. Cannot apply rubric automatically.</p>
      <button onClick={generate} disabled={loading}>{loading ? '...' : 'Generate Suggestion'}</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {data && (
        <div style={{ marginTop: 12, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
          <p>Status: {String(data.status)}</p>
          {data.suggestions && <pre>{JSON.stringify(data.suggestions, null, 2)}</pre>}
        </div>
      )}
    </div>
  )
}
