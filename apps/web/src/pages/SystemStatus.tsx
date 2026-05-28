import { useState, useEffect } from 'react'
import { fetchJson } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

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

  if (error && !product) return <ErrorDisplay message={error} onRetry={() => { setError(''); window.location.reload() }} />
  if (!product || !localApp || !runtime || !provider) return <LoadingSpinner label="Loading system status..." />

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">System Status</h2>
      <button
        className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700"
        type="button"
        onClick={() => onNavigate?.('weekly')}
      >
        Start Weekly Review
      </button>
      <h3 className="text-base font-medium">Local App</h3>
      <div className="space-y-1 text-sm text-gray-300">
        <p>Runtime mode: {String(runtime.mode)}</p>
        <p>Config path: {String(runtime.config_path)}</p>
        <p>Product data dir: {String(runtime.product_data_dir)}</p>
        <p>Frontend available: {localApp.frontend_available ? 'Yes' : 'No'}</p>
        <p>Provider mode: {String(provider.provider_mode)}</p>
      </div>
      <h3 className="text-base font-medium">P6 State</h3>
      <div className="space-y-1 text-sm text-gray-300">
        <p>Runtime: CODE_COMPLETE</p>
        <p>Behavior validation: NOT_VALIDATED</p>
        <p>Seal: NOT_SEALED</p>
      </div>
      <h3 className="text-base font-medium">Product Surface</h3>
      <div className="space-y-1 text-sm text-gray-300">
        <p>Phase 3: {String(product.phase3_status)}</p>
        <p>Phase 4: {String(product.phase4_status)}</p>
        <p>Storage: {String(product.storage_backend)}</p>
        <p>No secrets exposed: {product.no_secrets_exposed ? 'Yes' : 'No'}</p>
      </div>
      <h3 className="text-base font-medium">Safe Endpoints</h3>
      <ul className="list-disc list-inside text-sm text-gray-300">
        {(product.safe_public_endpoints as string[]).map(e => <li key={e}>{e}</li>)}
      </ul>
    </div>
  )
}
