import { useState, useEffect } from 'react'
import { fetchJson } from '../api'

export default function SystemStatus() {
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchJson('/product/status')
      .then(setData)
      .catch(e => setError(e.message))
  }, [])

  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>
  if (!data) return <p>Loading...</p>

  return (
    <div>
      <h2>System Status</h2>
      <p>Phase 3: {String(data.phase3_status)}</p>
      <p>Phase 4: {String(data.phase4_status)}</p>
      <p>Provider: {String(data.provider_gateway_status)}</p>
      <p>Storage: {String(data.storage_backend)}</p>
      <p>No secrets exposed: {data.no_secrets_exposed ? 'Yes' : 'No'}</p>
      <h3>Safe Endpoints</h3>
      <ul>{(data.safe_public_endpoints as string[]).map(e => <li key={e}>{e}</li>)}</ul>
    </div>
  )
}
