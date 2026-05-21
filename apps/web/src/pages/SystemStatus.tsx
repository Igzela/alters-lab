import { useState, useEffect } from 'react'
import { fetchJson } from '../api'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider'

export default function SystemStatus({ onNavigate }: { onNavigate?: (page: Page) => void }) {
  const [product, setProduct] = useState<Record<string, unknown> | null>(null)
  const [localApp, setLocalApp] = useState<Record<string, unknown> | null>(null)
  const [runtime, setRuntime] = useState<Record<string, unknown> | null>(null)
  const [provider, setProvider] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      fetchJson('/product/status'),
      fetchJson('/local-app/status'),
      fetchJson('/runtime-layout/status'),
      fetchJson('/provider-config/status'),
    ])
      .then(([nextProduct, nextLocalApp, nextRuntime, nextProvider]) => {
        setProduct(nextProduct)
        setLocalApp(nextLocalApp)
        setRuntime(nextRuntime)
        setProvider(nextProvider)
      })
      .catch(e => setError(e.message))
  }, [])

  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>
  if (!product || !localApp || !runtime || !provider) return <p>Loading...</p>

  return (
    <div>
      <h2>System Status</h2>
      <button
        style={{ padding: '8px 12px', border: '1px solid #333', borderRadius: 4, background: '#333', color: '#fff', cursor: 'pointer' }}
        type="button"
        onClick={() => onNavigate?.('weekly')}
      >
        Start Weekly Review
      </button>
      <h3>Local App</h3>
      <p>Runtime mode: {String(runtime.mode)}</p>
      <p>Config path: {String(runtime.config_path)}</p>
      <p>Product data dir: {String(runtime.product_data_dir)}</p>
      <p>Frontend available: {localApp.frontend_available ? 'Yes' : 'No'}</p>
      <p>Provider mode: {String(provider.provider_mode)}</p>
      <h3>P6 State</h3>
      <p>Runtime: CODE_COMPLETE</p>
      <p>Behavior validation: NOT_VALIDATED</p>
      <p>Seal: NOT_SEALED</p>
      <h3>Product Surface</h3>
      <p>Phase 3: {String(product.phase3_status)}</p>
      <p>Phase 4: {String(product.phase4_status)}</p>
      <p>Storage: {String(product.storage_backend)}</p>
      <p>No secrets exposed: {product.no_secrets_exposed ? 'Yes' : 'No'}</p>
      <h3>Safe Endpoints</h3>
      <ul>{(product.safe_public_endpoints as string[]).map(e => <li key={e}>{e}</li>)}</ul>
    </div>
  )
}
