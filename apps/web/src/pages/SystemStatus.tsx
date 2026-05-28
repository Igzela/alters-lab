import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson } from '../api'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
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
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('status.title')}</h2>
      <Button variant="primary" onClick={() => onNavigate?.('weekly')}>
        {t('status.startWeeklyReview')}
      </Button>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('status.localApp')}</h3>
        <div className="space-y-1 text-sm" style={{ color: '#c4c2b8' }}>
          <p>{t('status.runtimeMode')} <Badge variant="info">{String(runtime.mode)}</Badge></p>
          <p>{t('status.configPath')} <span style={{ color: '#7c7c6f' }}>{String(runtime.config_path)}</span></p>
          <p>{t('status.productDataDir')} <span style={{ color: '#7c7c6f' }}>{String(runtime.product_data_dir)}</span></p>
          <p>{t('status.frontendAvailable')} <Badge variant={localApp.frontend_available ? 'success' : 'error'}>{localApp.frontend_available ? 'Yes' : 'No'}</Badge></p>
          <p>{t('status.providerMode')} <Badge variant="info">{String(provider.provider_mode)}</Badge></p>
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('status.p6State')}</h3>
        <div className="space-y-1 text-sm" style={{ color: '#c4c2b8' }}>
          <p>{t('status.runtime')} <Badge variant="info">CODE_COMPLETE</Badge></p>
          <p>{t('status.behaviorValidation')} <Badge variant="warning">NOT_VALIDATED</Badge></p>
          <p>{t('status.seal')} <Badge variant="muted">NOT_SEALED</Badge></p>
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('status.productSurface')}</h3>
        <div className="space-y-1 text-sm" style={{ color: '#c4c2b8' }}>
          <p>{t('status.phase3')} <Badge variant="success">{String(product.phase3_status)}</Badge></p>
          <p>{t('status.phase4')} <Badge variant="success">{String(product.phase4_status)}</Badge></p>
          <p>{t('status.storage')} <Badge variant="info">{String(product.storage_backend)}</Badge></p>
          <p>{t('status.noSecretsExposed')} <Badge variant={product.no_secrets_exposed ? 'success' : 'error'}>{product.no_secrets_exposed ? 'Yes' : 'No'}</Badge></p>
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('status.safeEndpoints')}</h3>
        <ul className="list-disc list-inside text-sm" style={{ color: '#c4c2b8' }}>
          {(product.safe_public_endpoints as string[]).map(e => <li key={e}>{e}</li>)}
        </ul>
      </Card>
    </div>
  )
}
