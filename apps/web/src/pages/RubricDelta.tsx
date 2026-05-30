import { useTranslation } from 'react-i18next'
import { useSuggestRubricDelta } from '../hooks/useApi'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import ErrorDisplay from '../components/ErrorDisplay'

export default function RubricDelta() {
  const { t } = useTranslation()
  const mutation = useSuggestRubricDelta()

  const generate = () => mutation.mutate({ caller: 'api' })

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('rubricDelta.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('rubricDelta.description')}</p>
      <Button variant="primary" onClick={generate} disabled={mutation.isPending}>
        {mutation.isPending ? t('common.generating') : t('rubricDelta.generate')}
      </Button>
      {mutation.error && <ErrorDisplay message={(mutation.error as Error).message} />}
      {mutation.data && (
        <Card accent="amber">
          <p className="text-sm">{t('rubricDelta.status')} {String((mutation.data as Record<string, unknown>).status)}</p>
          <pre className="text-xs mt-2 whitespace-pre-wrap overflow-auto max-h-[400px] p-3 rounded-lg font-mono" style={{ color: 'var(--color-text-secondary)', backgroundColor: 'var(--color-surface-raised)', border: '1px solid var(--color-border)' }}>
            {(mutation.data as Record<string, unknown>).suggestions ? JSON.stringify((mutation.data as Record<string, unknown>).suggestions as Record<string, unknown>, null, 2) : ''}
          </pre>
        </Card>
      )}
    </div>
  )
}
