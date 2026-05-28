import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { deleteJson, fetchJson, postJson } from '../api'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input, Field, Select } from '../components/Input'
import { Badge } from '../components/Badge'
import { Banner } from '../components/Banner'
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
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('provider.title')}</h2>
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
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('provider.title')}</h2>

      <Banner variant="info">
        <strong>{t('provider.safetyNotes')}</strong>
        <ul className="mt-1.5 ml-4 list-disc space-y-0.5 text-xs">
          <li>{t('provider.disabledDefault')}</li>
          <li>{t('provider.mockMode')}</li>
          <li>{t('provider.liveMode')}</li>
          <li>{t('provider.outputAdvisory')}</li>
          <li>{t('provider.keyNeverDisplayed')}</li>
          <li>See <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SETUP.md" className="underline" style={{ color: '#00bae2' }}>{t('provider.providerSetup')}</a> and <a href="https://github.com/Igzela/alters-lab/blob/main/docs/user/PROVIDER_SAFETY.md" className="underline" style={{ color: '#00bae2' }}>{t('provider.providerSafety')}</a> for details</li>
        </ul>
      </Banner>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('provider.status')}</h3>
        <div className="text-sm space-y-1" style={{ color: '#c4c2b8' }}>
          <p>{t('provider.mode')} <Badge variant="info">{status.provider_mode}</Badge></p>
          <p>{t('provider.configured')} <Badge variant={status.configured ? 'success' : 'muted'}>{status.configured ? t('provider.yes') : t('provider.no')}</Badge></p>
          <p>{t('provider.baseUrl')} <Badge variant={status.base_url_configured ? 'success' : 'warning'}>{status.base_url_configured ? t('provider.configuredLabel') : t('provider.missing')}</Badge></p>
          <p>{t('provider.model')} <Badge variant={status.model_configured ? 'success' : 'warning'}>{status.model_configured ? t('provider.configuredLabel') : t('provider.missing')}</Badge></p>
          <p>{t('provider.apiKey')} <Badge variant={status.api_key_configured ? 'success' : 'warning'}>{status.api_key_configured ? t('provider.stored') : t('provider.notStored')}</Badge></p>
          <p>{t('provider.secretStorage')} <Badge variant="info">{status.secret_storage}</Badge></p>
          <p>{t('provider.secretsRedacted')} <Badge variant={status.secrets_redacted ? 'success' : 'muted'}>{status.secrets_redacted ? t('provider.yes') : t('provider.no')}</Badge></p>
          <p>{t('provider.outputPersists')} <Badge variant={status.provider_output_persists_by_default ? 'success' : 'muted'}>{status.provider_output_persists_by_default ? t('provider.yes') : t('provider.no')}</Badge></p>
          <p>{t('provider.canWriteYaml')} <Badge variant={status.provider_output_can_write_active_yaml ? 'warning' : 'muted'}>{status.provider_output_can_write_active_yaml ? t('provider.yes') : t('provider.no')}</Badge></p>
          <p>{t('provider.canGenerateScore')} <Badge variant={status.provider_output_can_generate_reality_score ? 'info' : 'muted'}>{status.provider_output_can_generate_reality_score ? t('provider.yes') : t('provider.no')}</Badge></p>
          <p>{t('provider.p6Validated')} <Badge variant={status.p6_behavior_validated ? 'success' : 'muted'}>{status.p6_behavior_validated ? t('provider.yes') : t('provider.no')}</Badge></p>
          <p>{t('provider.p6Sealed')} <Badge variant={status.p6_sealed ? 'success' : 'muted'}>{status.p6_sealed ? t('provider.yes') : t('provider.no')}</Badge></p>
        </div>
      </Card>

      <form onSubmit={saveConfig}>
        {hasUnsavedChanges && <Banner variant="warning">{t('provider.unsavedChanges')}</Banner>}
        <Field label={t('provider.modeLabel')}>
          <Select value={config.mode} onChange={e => updateConfig({ mode: e.target.value as ProviderMode })}>
            <option value="disabled">disabled</option>
            <option value="mock">mock</option>
            <option value="openai-compatible-http">openai-compatible-http</option>
          </Select>
        </Field>
        <Field label={t('provider.baseUrlLabel')}>
          <Input value={config.base_url || ''} onChange={e => updateConfig({ base_url: e.target.value })} placeholder="https://provider.example/v1" />
        </Field>
        <Field label={t('provider.modelLabel')}>
          <Input value={config.model || ''} onChange={e => updateConfig({ model: e.target.value })} placeholder="model-name" />
        </Field>
        <Field label={t('provider.timeoutLabel')}>
          <Input type="number" min={1} max={600} value={config.timeout_seconds} onChange={e => updateConfig({ timeout_seconds: Number(e.target.value) })} />
        </Field>
        <Field label={t('provider.secretStorageLabel')}>
          <Select value={config.secret_storage} onChange={e => updateConfig({ secret_storage: e.target.value as SecretStorage })}>
            <option value="keyring">keyring</option>
            <option value="secrets_yaml_fallback">secrets_yaml_fallback</option>
          </Select>
        </Field>
        <Button variant="primary" type="submit" disabled={saving}>
          {saving ? t('provider.saving') : t('provider.saveConfig')}
        </Button>
      </form>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('provider.apiKeyLabel')}</h3>
        <Field label={t('provider.keyLabel')}>
          <Input type="password" autoComplete="off" value={apiKey} onChange={e => setApiKey(e.target.value)} />
        </Field>
        <div className="flex gap-2">
          <Button variant="primary" onClick={storeSecret} disabled={storing || !apiKey.trim()}>
            {storing ? t('provider.storing') : t('provider.storeKey')}
          </Button>
          <Button variant="danger" onClick={deleteSecret} disabled={storing}>
            {storing ? t('provider.deleting') : t('provider.deleteKey')}
          </Button>
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('provider.dryRun')}</h3>
        <Button
          variant="secondary"
          onClick={testProvider}
          disabled={hasUnsavedChanges || testing}
        >
          {testing ? t('provider.testing') : t('provider.testConfig')}
        </Button>
        {hasUnsavedChanges && <p className="text-sm mt-1" style={{ color: '#7c7c6f' }}>{t('provider.saveBeforeTest')}</p>}
        {testResult && (
          <div className="mt-3 text-sm space-y-1" style={{ color: '#c4c2b8' }}>
            <p>Status: <Badge variant={testResult.provider_ready ? 'success' : 'error'}>{testResult.status}</Badge></p>
            <p>{t('provider.ready')} <Badge variant={testResult.provider_ready ? 'success' : 'muted'}>{testResult.provider_ready ? t('provider.yes') : t('provider.no')}</Badge></p>
            <p>{t('provider.networkCall')} <Badge variant={testResult.network_call_made ? 'info' : 'muted'}>{testResult.network_call_made ? t('provider.yes') : t('provider.no')}</Badge></p>
            <p>{testResult.message}</p>
          </div>
        )}
      </Card>

      {message && <Banner variant="success">{message}</Banner>}
    </div>
  )
}
