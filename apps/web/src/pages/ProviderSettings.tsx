import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
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
  const { t } = useTranslation()
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
      .then(() => { setMessage(t('provider.configSaved')); load() })
      .catch(e => setError(e instanceof Error ? e.message : t('provider.failedSave')))
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
      .then(() => { setApiKey(''); setMessage(t('provider.secretStored')); load() })
      .catch(e => setError(e instanceof Error ? e.message : t('provider.failedStore')))
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
      .then(() => { setApiKey(''); setMessage(t('provider.secretDeleted')); load() })
      .catch(e => setError(e instanceof Error ? e.message : t('provider.failedDelete')))
      .finally(() => setStoring(false))
  }

  if (error && !config) return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{t('provider.title')}</h2>
      <ErrorDisplay message={error} onRetry={load} />
    </div>
  )
  if (!config || !status) return <LoadingSpinner label={t('provider.loading')} />

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
      .catch(e => setError(e instanceof Error ? e.message : t('provider.testFailed')))
      .finally(() => setTesting(false))
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{t('provider.title')}</h2>

      <section className="mb-4 p-3 border border-gray-600 rounded-lg text-xs text-gray-400">
        <strong className="text-white">{t('provider.safetyNotes')}</strong>
        <ul className="mt-1.5 ml-4 list-disc space-y-0.5">
          <li>{t('provider.disabledDefault')}</li>
          <li>{t('provider.mockMode')}</li>
          <li>{t('provider.liveMode')}</li>
          <li>{t('provider.outputAdvisory')}</li>
          <li>{t('provider.keyNeverDisplayed')}</li>
          <li>See <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SETUP.md" className="text-blue-400 hover:text-blue-300">{t('provider.providerSetup')}</a> and <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SAFETY.md" className="text-blue-400 hover:text-blue-300">{t('provider.providerSafety')}</a> for details</li>
        </ul>
      </section>

      <section>
        <h3 className="text-base font-medium mb-2">{t('provider.status')}</h3>
        <div className="text-sm text-gray-300 space-y-1">
          <p>{t('provider.mode')} {status.provider_mode}</p>
          <p>{t('provider.configured')} {status.configured ? t('provider.yes') : t('provider.no')}</p>
          <p>{t('provider.baseUrl')} {status.base_url_configured ? t('provider.configuredLabel') : t('provider.missing')}</p>
          <p>{t('provider.model')} {status.model_configured ? t('provider.configuredLabel') : t('provider.missing')}</p>
          <p>{t('provider.apiKey')} {status.api_key_configured ? t('provider.stored') : t('provider.notStored')}</p>
          <p>{t('provider.secretStorage')} {status.secret_storage}</p>
          <p>{t('provider.secretsRedacted')} {status.secrets_redacted ? t('provider.yes') : t('provider.no')}</p>
          <p>{t('provider.outputPersists')} {status.provider_output_persists_by_default ? t('provider.yes') : t('provider.no')}</p>
          <p>{t('provider.canWriteYaml')} {status.provider_output_can_write_active_yaml ? t('provider.yes') : t('provider.no')}</p>
          <p>{t('provider.canGenerateScore')} {status.provider_output_can_generate_reality_score ? t('provider.yes') : t('provider.no')}</p>
          <p>{t('provider.p6Validated')} {status.p6_behavior_validated ? t('provider.yes') : t('provider.no')}</p>
          <p>{t('provider.p6Sealed')} {status.p6_sealed ? t('provider.yes') : t('provider.no')}</p>
        </div>
      </section>

      <form onSubmit={saveConfig}>
        {hasUnsavedChanges && <p className="text-amber-400 text-sm mb-2">{t('provider.unsavedChanges')}</p>}
        <label className={field}>
          <span className="text-sm text-gray-300">{t('provider.modeLabel')}</span>
          <select className={input} value={config.mode} onChange={e => updateConfig({ mode: e.target.value as ProviderMode })}>
            <option value="disabled">disabled</option>
            <option value="mock">mock</option>
            <option value="openai-compatible-http">openai-compatible-http</option>
          </select>
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">{t('provider.baseUrlLabel')}</span>
          <input className={input} value={config.base_url || ''} onChange={e => updateConfig({ base_url: e.target.value })} placeholder="https://provider.example/v1" />
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">{t('provider.modelLabel')}</span>
          <input className={input} value={config.model || ''} onChange={e => updateConfig({ model: e.target.value })} placeholder="model-name" />
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">{t('provider.timeoutLabel')}</span>
          <input className={input} type="number" min={1} max={600} value={config.timeout_seconds} onChange={e => updateConfig({ timeout_seconds: Number(e.target.value) })} />
        </label>
        <label className={field}>
          <span className="text-sm text-gray-300">{t('provider.secretStorageLabel')}</span>
          <select className={input} value={config.secret_storage} onChange={e => updateConfig({ secret_storage: e.target.value as SecretStorage })}>
            <option value="keyring">keyring</option>
            <option value="secrets_yaml_fallback">secrets_yaml_fallback</option>
          </select>
        </label>
        <button className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50" type="submit" disabled={saving}>
          {saving ? t('provider.saving') : t('provider.saveConfig')}
        </button>
      </form>

      <section>
        <h3 className="text-base font-medium mb-2">{t('provider.apiKeyLabel')}</h3>
        <label className={field}>
          <span className="text-sm text-gray-300">{t('provider.keyLabel')}</span>
          <input className={input} type="password" autoComplete="off" value={apiKey} onChange={e => setApiKey(e.target.value)} />
        </label>
        <div className="flex gap-2">
          <button className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50" type="button" onClick={storeSecret} disabled={storing || !apiKey.trim()}>
            {storing ? t('provider.storing') : t('provider.storeKey')}
          </button>
          <button className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50" type="button" onClick={deleteSecret} disabled={storing}>
            {storing ? t('provider.deleting') : t('provider.deleteKey')}
          </button>
        </div>
      </section>

      <section>
        <h3 className="text-base font-medium mb-2">{t('provider.dryRun')}</h3>
        <button
          className={`px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 ${hasUnsavedChanges || testing ? 'opacity-50' : ''}`}
          type="button"
          onClick={testProvider}
          disabled={hasUnsavedChanges || testing}
        >
          {testing ? t('provider.testing') : t('provider.testConfig')}
        </button>
        {hasUnsavedChanges && <p className="text-sm text-gray-400 mt-1">{t('provider.saveBeforeTest')}</p>}
        {testResult && (
          <div className="mt-3 text-sm text-gray-300 space-y-1">
            <p>Status: {testResult.status}</p>
            <p>{t('provider.ready')} {testResult.provider_ready ? t('provider.yes') : t('provider.no')}</p>
            <p>{t('provider.networkCall')} {testResult.network_call_made ? t('provider.yes') : t('provider.no')}</p>
            <p>{testResult.message}</p>
          </div>
        )}
      </section>

      {message && <p className="text-green-400 text-sm">{message}</p>}
    </div>
  )
}
