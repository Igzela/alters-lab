import { useTranslation } from 'react-i18next'
import { useGenerateCheckpointPlan } from '../hooks/useApi'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import ErrorDisplay from '../components/ErrorDisplay'

interface PlanStep {
  step_id: string
  title: string
  description: string
}

interface PlanData {
  status: string
  steps: PlanStep[]
  trigger_reason?: string
  recommended_scope?: string
}

interface MutationResult {
  status: string
  plan: PlanData | null
}

const statusVariant: Record<string, 'success' | 'warning' | 'error' | 'info' | 'amber' | 'muted'> = {
  pending_review: 'amber',
  saved: 'success',
  no_action: 'muted',
  generated: 'info',
}

export default function CheckpointPlan() {
  const { t } = useTranslation()
  const mutation = useGenerateCheckpointPlan()

  const generate = () => mutation.mutate({ caller: 'api' })

  const data = mutation.data as MutationResult | undefined

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('checkpointPlan.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('checkpointPlan.description')}</p>
      <Button variant="primary" onClick={generate} disabled={mutation.isPending}>
        {mutation.isPending ? t('common.generating') : t('checkpointPlan.generate')}
      </Button>
      {mutation.error && <ErrorDisplay message={(mutation.error as Error).message} />}
      {data && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-medium">{t('checkpointPlan.status')}</span>
            <Badge variant={statusVariant[data.status] ?? 'muted'}>{data.status}</Badge>
          </div>

          {data.plan ? (
            <div className="space-y-3">
              {data.plan.trigger_reason && (
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{data.plan.trigger_reason}</p>
              )}
              <h3 className="text-sm font-semibold">{t('checkpointPlan.steps')}</h3>
              <ol className="space-y-3 list-none">
                {data.plan.steps.map((step, idx) => (
                  <li key={step.step_id} className="rounded-lg p-3" style={{ backgroundColor: 'var(--color-surface-raised)', border: '1px solid var(--color-border)' }}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold" style={{ color: 'var(--color-text-secondary)' }}>{idx + 1}.</span>
                      <span className="text-sm font-semibold">{step.title}</span>
                    </div>
                    <p className="text-xs ml-5" style={{ color: 'var(--color-text-secondary)' }}>{step.description}</p>
                  </li>
                ))}
              </ol>
            </div>
          ) : (
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('checkpointPlan.noPlan')}</p>
          )}
        </Card>
      )}
    </div>
  )
}
