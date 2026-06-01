import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useOutcomeTargets, useCreateOutcomeTarget, useEvaluateOutcomeTarget } from '../hooks/usePredictionHooks'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Field, Input, Select, TextArea } from '../components/Input'
import { Banner } from '../components/Banner'
import { Badge } from '../components/Badge'
import { Skeleton } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'

const DOMAINS = ['career_education', 'financial', 'health', 'relationship', 'subjective_wellbeing'] as const
const STATUS_VARIANTS: Record<string, 'info' | 'success' | 'error' | 'warning' | 'muted'> = {
  planned: 'info',
  active: 'warning',
  achieved: 'success',
  missed: 'error',
  abandoned: 'muted',
}

export default function OutcomeTargets() {
  const { t } = useTranslation()
  const targetsQuery = useOutcomeTargets()
  const createMutation = useCreateOutcomeTarget()
  const evaluateMutation = useEvaluateOutcomeTarget()
  const [showForm, setShowForm] = useState(false)
  const [status, setStatus] = useState('')
  const [evalTargetId, setEvalTargetId] = useState<string | null>(null)
  const [evalValue, setEvalValue] = useState('')
  const [evalAchieved, setEvalAchieved] = useState(false)

  const [form, setForm] = useState({
    branch_id: '',
    domain: 'career_education' as string,
    horizon_months: 6,
    outcome_name: '',
    objective_definition: '',
    success_threshold: '',
    measurement_method: '',
    baseline_value: '',
    target_value: '',
  })

  const targets: Record<string, unknown>[] = (targetsQuery.data as Record<string, unknown> | undefined)?.targets as Record<string, unknown>[] || []

  const submit = () => {
    setStatus('')
    const payload: Record<string, unknown> = {
      branch_id: form.branch_id,
      domain: form.domain,
      horizon_months: form.horizon_months,
      outcome_name: form.outcome_name,
      objective_definition: form.objective_definition,
      success_threshold: form.success_threshold,
      measurement_method: form.measurement_method,
    }
    if (form.baseline_value) payload.baseline_value = form.baseline_value
    if (form.target_value) payload.target_value = form.target_value

    createMutation.mutate(payload, {
      onSuccess: () => {
        setStatus(t('outcomeTargets.created'))
        setShowForm(false)
        setForm({ branch_id: '', domain: 'career_education', horizon_months: 6, outcome_name: '', objective_definition: '', success_threshold: '', measurement_method: '', baseline_value: '', target_value: '' })
      },
    })
  }

  const submitEvaluation = () => {
    if (!evalTargetId) return
    evaluateMutation.mutate(
      { targetId: evalTargetId, body: { final_observed_value: evalValue, achieved: evalAchieved } },
      {
        onSuccess: () => {
          setEvalTargetId(null)
          setEvalValue('')
          setEvalAchieved(false)
        },
      }
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('outcomeTargets.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('outcomeTargets.description')}</p>

      {targetsQuery.isLoading && <Skeleton lines={4} />}
      {targetsQuery.error && <ErrorDisplay message={(targetsQuery.error as Error).message} onRetry={() => targetsQuery.refetch()} />}

      {targets.length === 0 && !targetsQuery.isLoading && (
        <Card>
          <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>{t('outcomeTargets.empty')}</p>
        </Card>
      )}

      {targets.map((target) => (
        <Card key={target.target_id as string} accent={target.status === 'achieved' ? 'green' : target.status === 'missed' ? 'red' : 'amber'}>
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-sm">{target.outcome_name as string}</span>
            <Badge variant={STATUS_VARIANTS[target.status as string] || 'muted'}>{target.status as string}</Badge>
          </div>
          <div className="text-xs space-y-1" style={{ color: 'var(--color-text-secondary)' }}>
            <div><strong>{t('outcomeTargets.branch')}:</strong> {target.branch_id as string}</div>
            <div><strong>{t('outcomeTargets.domain')}:</strong> {(target.domain as string).replace(/_/g, ' ')}</div>
            <div><strong>{t('outcomeTargets.objective')}:</strong> {target.objective_definition as string}</div>
            <div><strong>{t('outcomeTargets.threshold')}:</strong> {target.success_threshold as string}</div>
            <div><strong>{t('outcomeTargets.measurement')}:</strong> {target.measurement_method as string}</div>
            {target.baseline_value != null && <div><strong>{t('outcomeTargets.baseline')}:</strong> {String(target.baseline_value)}</div>}
            {target.target_value != null && <div><strong>{t('outcomeTargets.target')}:</strong> {String(target.target_value)}</div>}
            {target.final_observed_value != null && <div><strong>{t('outcomeTargets.observed')}:</strong> {String(target.final_observed_value)}</div>}
          </div>
          {(target.status === 'planned' || target.status === 'active') && (
            <div className="mt-2">
              {evalTargetId === target.target_id ? (
                <div className="space-y-2">
                  <Input
                    value={evalValue}
                    onChange={e => setEvalValue(e.target.value)}
                    placeholder={t('outcomeTargets.observedPlaceholder')}
                  />
                  <label className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                    <input type="checkbox" checked={evalAchieved} onChange={e => setEvalAchieved(e.target.checked)} />
                    {t('outcomeTargets.markAchieved')}
                  </label>
                  <div className="flex gap-2">
                    <Button variant="primary" onClick={submitEvaluation} disabled={evaluateMutation.isPending}>
                      {evaluateMutation.isPending ? t('common.sending') : t('outcomeTargets.submitEval')}
                    </Button>
                    <Button variant="ghost" onClick={() => setEvalTargetId(null)}>{t('common.dismiss')}</Button>
                  </div>
                  {evaluateMutation.error && <ErrorDisplay message={(evaluateMutation.error as Error).message} />}
                </div>
              ) : (
                <Button variant="secondary" onClick={() => setEvalTargetId(target.target_id as string)}>
                  {t('outcomeTargets.evaluate')}
                </Button>
              )}
            </div>
          )}
        </Card>
      ))}

      {!showForm && (
        <Button variant="primary" onClick={() => setShowForm(true)}>
          {t('outcomeTargets.create')}
        </Button>
      )}

      {showForm && (
        <Card accent="blue">
          <h3 className="text-sm font-semibold mb-3">{t('outcomeTargets.newTarget')}</h3>
          <div className="space-y-3">
            <Field label={t('outcomeTargets.branch')}>
              <Input value={form.branch_id} onChange={e => setForm({ ...form, branch_id: e.target.value })} placeholder="branch_A" />
            </Field>
            <Field label={t('outcomeTargets.domain')}>
              <Select value={form.domain} onChange={e => setForm({ ...form, domain: e.target.value })}>
                {DOMAINS.map(d => <option key={d} value={d}>{d.replace(/_/g, ' ')}</option>)}
              </Select>
            </Field>
            <Field label={t('outcomeTargets.horizon')}>
              <Input type="number" min={1} max={24} value={form.horizon_months} onChange={e => setForm({ ...form, horizon_months: parseInt(e.target.value) || 6 })} />
            </Field>
            <Field label={t('outcomeTargets.name')}>
              <Input value={form.outcome_name} onChange={e => setForm({ ...form, outcome_name: e.target.value })} />
            </Field>
            <Field label={t('outcomeTargets.objective')}>
              <TextArea value={form.objective_definition} onChange={e => setForm({ ...form, objective_definition: e.target.value })} rows={2} />
            </Field>
            <Field label={t('outcomeTargets.threshold')}>
              <TextArea value={form.success_threshold} onChange={e => setForm({ ...form, success_threshold: e.target.value })} rows={2} />
            </Field>
            <Field label={t('outcomeTargets.measurement')}>
              <Input value={form.measurement_method} onChange={e => setForm({ ...form, measurement_method: e.target.value })} />
            </Field>
            <Field label={t('outcomeTargets.baseline')}>
              <Input value={form.baseline_value} onChange={e => setForm({ ...form, baseline_value: e.target.value })} />
            </Field>
            <Field label={t('outcomeTargets.target')}>
              <Input value={form.target_value} onChange={e => setForm({ ...form, target_value: e.target.value })} />
            </Field>
          </div>
          <div className="flex gap-2 mt-3">
            <Button variant="primary" onClick={submit} disabled={createMutation.isPending}>
              {createMutation.isPending ? t('common.sending') : t('outcomeTargets.save')}
            </Button>
            <Button variant="ghost" onClick={() => setShowForm(false)}>{t('common.dismiss')}</Button>
          </div>
          {createMutation.error && <ErrorDisplay message={(createMutation.error as Error).message} />}
        </Card>
      )}

      {status && <Banner variant="success">{status}</Banner>}
    </div>
  )
}
