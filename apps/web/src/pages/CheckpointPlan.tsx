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
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Checkpoint Plan</h2>
      <p className="text-gray-500 text-xs">Plans are pending_review only. Cannot regenerate automatically.</p>
      <button
        className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50"
        onClick={generate}
        disabled={loading}
      >
        {loading ? '...' : 'Generate Plan'}
      </button>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {data && (
        <div className="mt-3 p-3 bg-gray-800/50 rounded border border-gray-700">
          <p className="text-sm">Status: {String(data.status)}</p>
          <pre className="text-xs text-gray-300 mt-2 whitespace-pre-wrap">
            {data.plan ? JSON.stringify(data.plan as Record<string, unknown>, null, 2) : ''}
          </pre>
        </div>
      )}
    </div>
  )
}
