import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider'

export default function SystemStatus({ onNavigate }: { onNavigate?: (page: Page) => void }) {
  const { t } = useTranslation()
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
  if (!product || !localApp || !runtime || !provider) return <LoadingSpinner label={t('status.loading')} />

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{t('status.title')}</h2>
      <button
        className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700"
        type="button"
        onClick={() => onNavigate?.('weekly')}
      >
        {t('status.startWeeklyReview')}
      </button>
      <h3 className="text-base font-medium">{t('status.localApp')}</h3>
      <div className="space-y-1 text-sm text-gray-300">
        <p>{t('status.runtimeMode')} {String(runtime.mode)}</p>
        <p>{t('status.configPath')} {String(runtime.config_path)}</p>
        <p>{t('status.productDataDir')} {String(runtime.product_data_dir)}</p>
        <p>{t('status.frontendAvailable')} {localApp.frontend_available ? 'Yes' : 'No'}</p>
        <p>{t('status.providerMode')} {String(provider.provider_mode)}</p>
      </div>
      <h3 className="text-base font-medium">{t('status.p6State')}</h3>
      <div className="space-y-1 text-sm text-gray-300">
        <p>{t('status.runtime')} CODE_COMPLETE</p>
        <p>{t('status.behaviorValidation')} NOT_VALIDATED</p>
        <p>{t('status.seal')} NOT_SEALED</p>
      </div>
      <h3 className="text-base font-medium">{t('status.productSurface')}</h3>
      <div className="space-y-1 text-sm text-gray-300">
        <p>{t('status.phase3')} {String(product.phase3_status)}</p>
        <p>{t('status.phase4')} {String(product.phase4_status)}</p>
        <p>{t('status.storage')} {String(product.storage_backend)}</p>
        <p>{t('status.noSecretsExposed')} {product.no_secrets_exposed ? 'Yes' : 'No'}</p>
      </div>
      <h3 className="text-base font-medium">{t('status.safeEndpoints')}</h3>
      <ul className="list-disc list-inside text-sm text-gray-300">
        {(product.safe_public_endpoints as string[]).map(e => <li key={e}>{e}</li>)}
      </ul>
    </div>
  )
}
