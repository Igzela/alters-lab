import { FormEvent, useCallback, useEffect, useState } from 'react'
import { deleteJson, fetchJson, postJson } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

type ProviderMode = 'disabled' | 'mock' | 'openai-compatible-http'
type SecretStorage = 'keyring' | 'secrets_yaml_fallback'

type ProviderConfig = {
  mode: ProviderMode
  base_url: string | null
  model: string | null
  timeout_seconds: number
  secret_storage: SecretStorage
  key_name: string
  keyring_available: boolean
  secrets_redacted: boolean
  provider_output_persists_by_default: boolean
  provider_output_can_write_active_yaml: boolean
  provider_output_can_generate_reality_score: boolean
  p6_behavior_validated: boolean
  p6_sealed: boolean
}

type ProviderStatus = {
  provider_mode: ProviderMode
  configured: boolean
  base_url_configured: boolean
  model_configured: boolean
  api_key_configured: boolean
  secret_storage: SecretStorage
  keyring_available: boolean
  secrets_redacted: boolean
  provider_output_persists_by_default: boolean
  provider_output_can_write_active_yaml: boolean
  provider_output_can_generate_reality_score: boolean
  p6_behavior_validated: boolean
  p6_sealed: boolean
}

type TestResult = {
  status: string
  provider_ready: boolean
  message: string
  network_call_made: boolean
}

const field = 'grid gap-1.5 mb-3'
const input = 'px-2.5 py-2 border border-gray-600 rounded text-sm bg-gray-800 text-white'

export default function ProviderSettings() {
  const [config, setConfig] = useState<ProviderConfig | null>(null)
  const [savedConfig, setSavedConfig] = useState<ProviderConfig | null>(null)
  const [status, setStatus] = useState<ProviderStatus | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [testResult, setTestResult] = useState<TestResult | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [storing, setStoring] = useState(false)
  const [testing, setTesting] = useState(false)

  const load = () => {
    setError('')
    Promise.all([
      fetchJson('/provider-config/config') as Promise<ProviderConfig>,
      fetchJson('/provider-config/status') as Promise<ProviderStatus>,
    ])
      .then(([nextConfig, nextStatus]) => {
        setConfig(nextConfig)
        setSavedConfig(nextConfig)
        setStatus(nextStatus)
      })
      .catch(e => setError(e.message))
  }

  useEffect(() => { load() }, [])

  const updateConfig = (patch: Partial<ProviderConfig>) => {
    if (!config) return
    setConfig({ ...config, ...patch })
  }

  const saveConfig = (event: FormEvent) => {
    event.preventDefault()
    if (!config) return
    setError('')
    setMessage('')
    setSaving(true)
    postJson('/provider-config/config', {
      mode: config.mode,
      base_url: config.base_url || null,
      model: config.model || null,
      timeout_seconds: config.timeout_seconds,
      secret_storage: config.secret_storage,
      key_name: config.key_name,
      explicit_user_configuration: config.mode === 'openai-compatible-http',
    })
      .then(() => { setMessage('Config saved'); load() })
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to save config'))
      .finally(() => setSaving(false))
  }

  const storeSecret = () => {
    if (!config || !apiKey.trim()) return
    setError('')
    setMessage('')
    setStoring(true)
    postJson('/provider-config/secret', {
      api_key: apiKey,
      storage: config.secret_storage,
      confirmation: 'store-secret',
    })
      .then(() => { setApiKey(''); setMessage('Secret stored'); load() })
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to store secret'))
      .finally(() => setStoring(false))
  }

  const deleteSecret = () => {
    if (!config) return
    setError('')
    setMessage('')
    setStoring(true)
    deleteJson('/provider-config/secret', {
      storage: config.secret_storage,
      confirmation: 'delete-secret',
    })
      .then(() => { setApiKey(''); setMessage('Secret deleted'); load() })
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to delete secret'))
      .finally(() => setStoring(false))
  }

  if (error && !config) return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Provider Settings</h2>
      <ErrorDisplay message={error} onRetry={load} />
    </div>
  )
  if (!config || !status) return <LoadingSpinner label="Loading provider settings..." />

  const hasUnsavedChanges = savedConfig
    ? JSON.stringify({
        mode: config.mode, base_url: config.base_url || null, model: config.model || null,
        timeout_seconds: config.timeout_seconds, secret_storage: config.secret_storage, key_name: config.key_name,
      }) !== JSON.stringify({
        mode: savedConfig.mode, base_url: savedConfig.base_url || null, model: savedConfig.model || null,
        timeout_seconds: savedConfig.timeout_seconds, secret_storage: savedConfig.secret_storage, key_name: savedConfig.key_name,
      })
    : false

  const testProvider = () => {
    if (hasUnsavedChanges) return
    setError('')
    setTesting(true)
    postJson('/provider-config/test', { dry_run: true })
      .then(result => setTestResult(result as TestResult))
      .catch(e => setError(e instanceof Error ? e.message : 'Provider test failed'))
      .finally(() => setTesting(false))
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Provider Settings</h2>

      <section className="mb-4 p-3 border border-gray-600 rounded-lg text-xs text-gray-400">
        <strong className="text-white">Safety notes:</strong>
        <ul className="mt-1.5 ml-4 list-disc space-y-0.5">
          <li>Default mode is <strong>disabled</strong> — no LLM calls, no API key needed</li>
          <li><strong>Mock</strong> mode: no network, no API key, simulated responses for testing</li>
          <li><strong>Live</strong> mode requires explicit configuration and confirmation before each network call</li>
          <li>Provider output is <strong>unverified and advisory only</strong></li>
          <li>API key is <strong>never displayed</strong> after storage</li>
          <li>See <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SETUP.md" className="text-blue-400 hover:text-blue-300">Provider Setup</a> and <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SAFETY.md" className="text-blue-400 hover:text-blue-300">Provider Safety</a> for details</li>
        </ul>
      </section>

      <section>
        <h3 className="text-base font-medium mb-2">Status</h3>
        <div className="text-sm text-gray-300 space-y-1">
          <p>Mode: {status.provider_mode}</p>
          <p>Configured: {status.configured ? 'Yes' : 'No'}</p>
          <p>Base URL: {status.base_url_configured ? 'Configured' : 'Missing'}</p>
          <p>Model: {status.model_configured ? 'Configured' : 'Missing'}</p>
          <p>API key: {status.api_key_configured ? 'Stored' : 'Not stored'}</p>
          <p>Secret storage: {status.secret_storage}</p>
          <p>Secrets redacted: {status.secrets_redacted ? 'Yes' : 'No'}</p>
          <p>Provider output persists by default: {status.provider_output_persists_by_default ? 'Yes' : 'No'}</p>
          <p>Provider can write active YAML: {status.provider_output_can_write_active_yaml ? 'Yes' : 'No'}</p>
          <p>Provider can generate reality score: {status.provider_output_can_generate_reality_score ? 'Yes' : 'No'}</p>
          <p>P6 behavior validated: {status.p6_behavior_validated ? 'Yes' : 'No'}</p>
          <p>P6 sealed: {status.p6_sealed ? 'Yes' : 'No'}</p>
        </div>
      </section>

      <form onSubmit={saveConfig}>
        {hasUnsavedChanges && <p className="text-amber-400 text-sm mb-2">Unsaved changes. Save config before testing.</p>}
        <label className={field}>
          <span className="text-sm text-gray-300">Mode</span>
          <select className={input} value={config.mode} onChange={e => updateConfig({ mode: e.target.value as ProviderMode })}>
            <option value="disabled">disabled</option>
            <option value="mock">mock</option>
            <option value="openai-compatible-http">openai-compatible-http</option>
          </select>
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">Base URL</span>
          <input className={input} value={config.base_url || ''} onChange={e => updateConfig({ base_url: e.target.value })} placeholder="https://provider.example/v1" />
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">Model</span>
          <input className={input} value={config.model || ''} onChange={e => updateConfig({ model: e.target.value })} placeholder="model-name" />
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">Timeout seconds</span>
          <input className={input} type="number" min={1} max={600} value={config.timeout_seconds} onChange={e => updateConfig({ timeout_seconds: Number(e.target.value) })} />
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">Secret storage</span>
          <select className={input} value={config.secret_storage} onChange={e => updateConfig({ secret_storage: e.target.value as SecretStorage })}>
            <option value="keyring">keyring</option>
            <option value="secrets_yaml_fallback">secrets_yaml_fallback</option>
          </select>
        </label>
        <button className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50" type="submit" disabled={saving}>
          {saving ? 'Saving...' : 'Save Config'}
        </button>
      </form>

      <section>
        <h3 className="text-base font-medium mb-2">API Key</h3>
        <label className={field}>
          <span className="text-sm text-gray-300">Key</span>
          <input className={input} type="password" autoComplete="off" value={apiKey} onChange={e => setApiKey(e.target.value)} />
        </label>
        <div className="flex gap-2">
          <button className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50" type="button" onClick={storeSecret} disabled={storing || !apiKey.trim()}>
            {storing ? 'Storing...' : 'Store Key'}
          </button>
          <button className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50" type="button" onClick={deleteSecret} disabled={storing}>
            {storing ? 'Deleting...' : 'Delete Key'}
          </button>
        </div>
      </section>

      <section>
        <h3 className="text-base font-medium mb-2">Dry Run</h3>
        <button
          className={`px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 ${hasUnsavedChanges || testing ? 'opacity-50' : ''}`}
          type="button"
          onClick={testProvider}
          disabled={hasUnsavedChanges || testing}
        >
          {testing ? 'Testing...' : 'Test Provider Config'}
        </button>
        {hasUnsavedChanges && <p className="text-sm text-gray-400 mt-1">Save config before testing.</p>}
        {testResult && (
          <div className="mt-3 text-sm text-gray-300 space-y-1">
            <p>Status: {testResult.status}</p>
            <p>Ready: {testResult.provider_ready ? 'Yes' : 'No'}</p>
            <p>Network call made: {testResult.network_call_made ? 'Yes' : 'No'}</p>
            <p>{testResult.message}</p>
          </div>
        )}
      </section>

      {message && <p className="text-green-400 text-sm">{message}</p>}
    </div>
  )
}
