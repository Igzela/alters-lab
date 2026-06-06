import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useProductStatus, useLocalAppStatus, useRuntimeStatus, useProviderStatus } from '../hooks/useApi'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { SkeletonCard } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'
import { useNavigation } from '../components/NavigationContext'

export default function SystemStatus() {
  const { t } = useTranslation()
  const { navigate } = useNavigation()
  const product = useProductStatus()
  const localApp = useLocalAppStatus()
  const runtime = useRuntimeStatus()
  const provider = useProviderStatus()
  const [showAdvanced, setShowAdvanced] = useState(false)

  const error = product.error || localApp.error || runtime.error || provider.error
  const isLoading = product.isLoading || localApp.isLoading || runtime.isLoading || provider.isLoading

  if (error && !product.data) return <ErrorDisplay message={(error as Error).message} onRetry={() => { product.refetch(); localApp.refetch(); runtime.refetch(); provider.refetch() }} />
  if (isLoading) return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('status.title')}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  )

  const allHealthy = product.data?.no_secrets_exposed && localApp.data?.frontend_available

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('status.title')}</h2>

      <Card>
        <div className="flex items-center gap-2 mb-3">
          <span className={`inline-block w-3 h-3 rounded-full ${allHealthy ? 'bg-green-500' : 'bg-yellow-500'}`} />
          <span className="text-sm font-medium">{allHealthy ? t('status.healthy') : t('status.degraded')}</span>
        </div>
        <div className="space-y-1 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          <p>{t('status.providerMode')} <Badge variant="info">{String(provider.data?.provider_mode)}</Badge></p>
          <p>{t('status.frontendAvailable')} <Badge variant={localApp.data?.frontend_available ? 'success' : 'error'}>{localApp.data?.frontend_available ? t('common.yes') : t('common.no')}</Badge></p>
        </div>
      </Card>

      <Button variant="primary" onClick={() => navigate('weekly')}>
        {t('status.startWeeklyReview')}
      </Button>

      <div>
        <button
          className="text-sm underline cursor-pointer"
          style={{ color: 'var(--color-text-muted)' }}
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? '▾' : '▸'} {t('status.advancedInfo')}
        </button>

        {showAdvanced && (
          <div className="mt-2 space-y-3">
            <Card>
              <h3 className="text-sm font-medium mb-2">{t('status.localApp')}</h3>
              <div className="space-y-1 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                <p>{t('status.runtimeMode')} <Badge variant="info">{String(runtime.data?.mode)}</Badge></p>
                <p>{t('status.configPath')} <span style={{ color: 'var(--color-text-muted)' }}>{String(runtime.data?.config_path)}</span></p>
                <p>{t('status.productDataDir')} <span style={{ color: 'var(--color-text-muted)' }}>{String(runtime.data?.product_data_dir)}</span></p>
              </div>
            </Card>

            <Card>
              <h3 className="text-sm font-medium mb-2">{t('status.productSurface')}</h3>
              <div className="space-y-1 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                <p>{t('status.storage')} <Badge variant="info">{String(product.data?.storage_backend)}</Badge></p>
                <p>{t('status.noSecretsExposed')} <Badge variant={product.data?.no_secrets_exposed ? 'success' : 'error'}>{product.data?.no_secrets_exposed ? t('common.yes') : t('common.no')}</Badge></p>
              </div>
            </Card>

            <Card>
              <h3 className="text-sm font-medium mb-2">{t('status.safeEndpoints')}</h3>
              <ul className="list-disc list-inside text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                {((product.data?.safe_public_endpoints as string[]) ?? []).map(e => <li key={e}>{e}</li>)}
              </ul>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
