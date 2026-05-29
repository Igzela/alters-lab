import { useTranslation } from 'react-i18next'
import { useProductStatus, useLocalAppStatus, useRuntimeStatus, useProviderStatus } from '../hooks/useApi'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { SkeletonCard } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started' | 'patterns' | 'validation' | 'data'

export default function SystemStatus({ onNavigate }: { onNavigate?: (page: Page) => void }) {
  const { t } = useTranslation()
  const product = useProductStatus()
  const localApp = useLocalAppStatus()
  const runtime = useRuntimeStatus()
  const provider = useProviderStatus()

  const error = product.error || localApp.error || runtime.error || provider.error
  const isLoading = product.isLoading || localApp.isLoading || runtime.isLoading || provider.isLoading

  if (error && !product.data) return <ErrorDisplay message={(error as Error).message} onRetry={() => { product.refetch(); localApp.refetch(); runtime.refetch(); provider.refetch() }} />
  if (isLoading) return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('status.title')}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  )

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('status.title')}</h2>
      <Button variant="primary" onClick={() => onNavigate?.('weekly')}>
        {t('status.startWeeklyReview')}
      </Button>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('status.localApp')}</h3>
        <div className="space-y-1 text-sm" style={{ color: '#78716c' }}>
          <p>{t('status.runtimeMode')} <Badge variant="info">{String(runtime.data?.mode)}</Badge></p>
          <p>{t('status.configPath')} <span style={{ color: '#a8a29e' }}>{String(runtime.data?.config_path)}</span></p>
          <p>{t('status.productDataDir')} <span style={{ color: '#a8a29e' }}>{String(runtime.data?.product_data_dir)}</span></p>
          <p>{t('status.frontendAvailable')} <Badge variant={localApp.data?.frontend_available ? 'success' : 'error'}>{localApp.data?.frontend_available ? t('common.yes') : t('common.no')}</Badge></p>
          <p>{t('status.providerMode')} <Badge variant="info">{String(provider.data?.provider_mode)}</Badge></p>
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('status.productSurface')}</h3>
        <div className="space-y-1 text-sm" style={{ color: '#78716c' }}>
          <p>{t('status.storage')} <Badge variant="info">{String(product.data?.storage_backend)}</Badge></p>
          <p>{t('status.noSecretsExposed')} <Badge variant={product.data?.no_secrets_exposed ? 'success' : 'error'}>{product.data?.no_secrets_exposed ? t('common.yes') : t('common.no')}</Badge></p>
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-medium mb-2">{t('status.safeEndpoints')}</h3>
        <ul className="list-disc list-inside text-sm" style={{ color: '#78716c' }}>
          {(product.data?.safe_public_endpoints as string[]).map(e => <li key={e}>{e}</li>)}
        </ul>
      </Card>
    </div>
  )
}
