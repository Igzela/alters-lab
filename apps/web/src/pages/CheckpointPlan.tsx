import { useTranslation } from 'react-i18next'
import { useGenerateCheckpointPlan } from '../hooks/useApi'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import ErrorDisplay from '../components/ErrorDisplay'

export default function CheckpointPlan() {
  const { t } = useTranslation()
  const mutation = useGenerateCheckpointPlan()

  const generate = () => mutation.mutate({ caller: 'api' })

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('checkpointPlan.title')}</h2>
      <p className="text-sm" style={{ color: '#78716c' }}>{t('checkpointPlan.description')}</p>
      <Button variant="primary" onClick={generate} disabled={mutation.isPending}>
        {mutation.isPending ? t('common.generating') : t('checkpointPlan.generate')}
      </Button>
      {mutation.error && <ErrorDisplay message={(mutation.error as Error).message} />}
      {mutation.data && (
        <Card>
          <p className="text-sm">{t('checkpointPlan.status')} {String((mutation.data as Record<string, unknown>).status)}</p>
          <pre className="text-xs mt-2 whitespace-pre-wrap overflow-auto max-h-[400px] p-3 rounded-lg font-mono" style={{ color: '#78716c', backgroundColor: '#f5f4f0', border: '1px solid #e8e6e1' }}>
            {(mutation.data as Record<string, unknown>).plan ? JSON.stringify((mutation.data as Record<string, unknown>).plan as Record<string, unknown>, null, 2) : ''}
          </pre>
        </Card>
      )}
    </div>
  )
}
