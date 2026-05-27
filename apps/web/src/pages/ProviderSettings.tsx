import { FormEvent, useEffect, useState } from 'react'
import { deleteJson, fetchJson, postJson } from '../api'

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

const fieldStyle = {
  display: 'grid',
  gap: 6,
  marginBottom: 12,
}

const inputStyle = {
  padding: '8px 10px',
  border: '1px solid #bbb',
  borderRadius: 4,
  fontSize: 14,
}

const buttonStyle = {
  padding: '8px 12px',
  border: '1px solid #333',
  borderRadius: 4,
  background: '#333',
  color: '#fff',
  cursor: 'pointer',
}

export default function ProviderSettings() {
  const [config, setConfig] = useState<ProviderConfig | null>(null)
  const [savedConfig, setSavedConfig] = useState<ProviderConfig | null>(null)
  const [status, setStatus] = useState<ProviderStatus | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [testResult, setTestResult] = useState<TestResult | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

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

  useEffect(() => {
    load()
  }, [])

  const updateConfig = (patch: Partial<ProviderConfig>) => {
    if (!config) return
    setConfig({ ...config, ...patch })
  }

  const saveConfig = (event: FormEvent) => {
    event.preventDefault()
    if (!config) return
    setError('')
    setMessage('')
    postJson('/provider-config/config', {
      mode: config.mode,
      base_url: config.base_url || null,
      model: config.model || null,
      timeout_seconds: config.timeout_seconds,
      secret_storage: config.secret_storage,
      key_name: config.key_name,
      explicit_user_configuration: config.mode === 'openai-compatible-http',
    })
      .then(() => {
        setMessage('Config saved')
        load()
      })
      .catch(e => setError(e.message))
  }

  const storeSecret = () => {
    if (!config || !apiKey.trim()) return
    setError('')
    setMessage('')
    postJson('/provider-config/secret', {
      api_key: apiKey,
      storage: config.secret_storage,
      confirmation: 'store-secret',
    })
      .then(() => {
        setApiKey('')
        setMessage('Secret stored')
        load()
      })
      .catch(e => setError(e.message))
  }

  const deleteSecret = () => {
    if (!config) return
    setError('')
    setMessage('')
    deleteJson('/provider-config/secret', {
      storage: config.secret_storage,
      confirmation: 'delete-secret',
    })
      .then(() => {
        setApiKey('')
        setMessage('Secret deleted')
        load()
      })
      .catch(e => setError(e.message))
  }

  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>
  if (!config || !status) return <p>Loading...</p>

  const hasUnsavedChanges = savedConfig
    ? JSON.stringify({
      mode: config.mode,
      base_url: config.base_url || null,
      model: config.model || null,
      timeout_seconds: config.timeout_seconds,
      secret_storage: config.secret_storage,
      key_name: config.key_name,
    }) !== JSON.stringify({
      mode: savedConfig.mode,
      base_url: savedConfig.base_url || null,
      model: savedConfig.model || null,
      timeout_seconds: savedConfig.timeout_seconds,
      secret_storage: savedConfig.secret_storage,
      key_name: savedConfig.key_name,
    })
    : false

  const testProvider = () => {
    if (hasUnsavedChanges) return
    setError('')
    postJson('/provider-config/test', { dry_run: true })
      .then(result => setTestResult(result as TestResult))
      .catch(e => setError(e.message))
  }

  return (
    <div>
      <h2>Provider Settings</h2>

      <section style={{ marginBottom: 16, padding: 12, border: '1px solid #444', borderRadius: 6, fontSize: 13, color: '#aaa' }}>
        <strong style={{ color: '#fff' }}>Safety notes:</strong>
        <ul style={{ margin: '6px 0 0 16px', padding: 0 }}>
          <li>Default mode is <strong>disabled</strong> — no LLM calls, no API key needed</li>
          <li><strong>Mock</strong> mode: no network, no API key, simulated responses for testing</li>
          <li><strong>Live</strong> mode requires explicit configuration and confirmation before each network call</li>
          <li>Provider output is <strong>unverified and advisory only</strong></li>
          <li>API key is <strong>never displayed</strong> after storage</li>
          <li>See <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SETUP.md" style={{ color: '#6ea8fe' }}>Provider Setup</a> and <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SAFETY.md" style={{ color: '#6ea8fe' }}>Provider Safety</a> for details</li>
        </ul>
      </section>

      <section style={{ marginBottom: 20 }}>
        <h3>Status</h3>
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
      </section>

      <form onSubmit={saveConfig} style={{ marginBottom: 20 }}>
        {hasUnsavedChanges && <p style={{ color: '#b45309' }}>Unsaved changes. Save config before testing.</p>}
        <label style={fieldStyle}>
          Mode
          <select
            style={inputStyle}
            value={config.mode}
            onChange={event => updateConfig({ mode: event.target.value as ProviderMode })}
          >
            <option value="disabled">disabled</option>
            <option value="mock">mock</option>
            <option value="openai-compatible-http">openai-compatible-http</option>
          </select>
        </label>

        <label style={fieldStyle}>
          Base URL
          <input
            style={inputStyle}
            value={config.base_url || ''}
            onChange={event => updateConfig({ base_url: event.target.value })}
            placeholder="https://provider.example/v1"
          />
        </label>

        <label style={fieldStyle}>
          Model
          <input
            style={inputStyle}
            value={config.model || ''}
            onChange={event => updateConfig({ model: event.target.value })}
            placeholder="model-name"
          />
        </label>

        <label style={fieldStyle}>
          Timeout seconds
          <input
            style={inputStyle}
            type="number"
            min={1}
            max={600}
            value={config.timeout_seconds}
            onChange={event => updateConfig({ timeout_seconds: Number(event.target.value) })}
          />
        </label>

        <label style={fieldStyle}>
          Secret storage
          <select
            style={inputStyle}
            value={config.secret_storage}
            onChange={event => updateConfig({ secret_storage: event.target.value as SecretStorage })}
          >
            <option value="keyring">keyring</option>
            <option value="secrets_yaml_fallback">secrets_yaml_fallback</option>
          </select>
        </label>

        <button style={buttonStyle} type="submit">Save Config</button>
      </form>

      <section style={{ marginBottom: 20 }}>
        <h3>API Key</h3>
        <label style={fieldStyle}>
          Key
          <input
            style={inputStyle}
            type="password"
            autoComplete="off"
            value={apiKey}
            onChange={event => setApiKey(event.target.value)}
          />
        </label>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button style={buttonStyle} type="button" onClick={storeSecret}>Store Key</button>
          <button style={{ ...buttonStyle, background: '#fff', color: '#333' }} type="button" onClick={deleteSecret}>
            Delete Key
          </button>
        </div>
      </section>

      <section>
        <h3>Dry Run</h3>
        <button
          style={{ ...buttonStyle, opacity: hasUnsavedChanges ? 0.5 : 1 }}
          type="button"
          onClick={testProvider}
          disabled={hasUnsavedChanges}
        >
          Test Provider Config
        </button>
        {hasUnsavedChanges && <p>Save config before testing.</p>}
        {testResult && (
          <div style={{ marginTop: 12 }}>
            <p>Status: {testResult.status}</p>
            <p>Ready: {testResult.provider_ready ? 'Yes' : 'No'}</p>
            <p>Network call made: {testResult.network_call_made ? 'Yes' : 'No'}</p>
            <p>{testResult.message}</p>
          </div>
        )}
      </section>

      {message && <p>{message}</p>}
    </div>
  )
}
