import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { usePredictorProfiles, useCreatePredictorProfile } from '../hooks/usePredictionHooks'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Field, Input, Select } from '../components/Input'
import { Banner } from '../components/Banner'
import { Badge } from '../components/Badge'
import { Skeleton } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'

const TRAITS = ['conscientiousness', 'neuroticism_negative_emotionality', 'extraversion', 'agreeableness', 'openness'] as const
const DOMAINS = ['career_education', 'financial', 'health', 'relationship', 'subjective_wellbeing'] as const

export default function PredictorProfile() {
  const { t } = useTranslation()
  const profilesQuery = usePredictorProfiles()
  const createMutation = useCreatePredictorProfile()
  const [showForm, setShowForm] = useState(false)
  const [status, setStatus] = useState('')

  const [traits, setTraits] = useState<Record<string, string>>({})
  const [traitSource, setTraitSource] = useState<'short_self_report' | 'manual_estimate' | 'unknown'>('short_self_report')
  const [context, setContext] = useState({ education_status: '', employment_status: '', financial_stability: '', relationship_status: '' })
  const [healthConstraints, setHealthConstraints] = useState('')
  const [selectedDomains, setSelectedDomains] = useState<string[]>(['career_education'])
  const [timeHorizon, setTimeHorizon] = useState(6)

  const profiles: Record<string, unknown>[] = (profilesQuery.data as Record<string, unknown> | undefined)?.profiles as Record<string, unknown>[] || []

  const toggleDomain = (d: string) => {
    setSelectedDomains(prev => prev.includes(d) ? prev.filter(x => x !== d) : [...prev, d])
  }

  const submit = () => {
    setStatus('')
    const traitBaseline: Record<string, unknown> = { source: traitSource }
    for (const t of TRAITS) {
      const v = traits[t]
      traitBaseline[t] = v === '' || v === undefined ? null : parseFloat(v)
    }
    const payload = {
      trait_baseline: traitBaseline,
      current_context: {
        education_status: context.education_status || null,
        employment_status: context.employment_status || null,
        financial_stability: context.financial_stability || null,
        relationship_status: context.relationship_status || null,
        health_constraints: healthConstraints ? healthConstraints.split(',').map(s => s.trim()).filter(Boolean) : [],
      },
      prediction_targets: {
        target_domains: selectedDomains,
        time_horizon_months: timeHorizon,
      },
    }
    createMutation.mutate(payload, {
      onSuccess: () => {
        setStatus(t('predictorProfile.created'))
        setShowForm(false)
        setTraits({})
        setContext({ education_status: '', employment_status: '', financial_stability: '', relationship_status: '' })
        setHealthConstraints('')
      },
    })
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('predictorProfile.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('predictorProfile.description')}</p>

      <Banner variant="warning">{t('predictorProfile.selfReportWarning')}</Banner>

      {profilesQuery.isLoading && <Skeleton lines={4} />}
      {profilesQuery.error && <ErrorDisplay message={(profilesQuery.error as Error).message} onRetry={() => profilesQuery.refetch()} />}

      {profiles.map((p) => (
        <Card key={p.profile_id as string} accent="amber">
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-sm">{p.profile_id as string}</span>
            <Badge variant={p.self_reported ? 'warning' : 'success'}>
              {p.self_reported ? t('predictorProfile.selfReported') : t('predictorProfile.objective')}
            </Badge>
          </div>
          <div className="text-xs space-y-1" style={{ color: 'var(--color-text-secondary)' }}>
            <div><strong>{t('predictorProfile.traitSource')}:</strong> {(p.trait_baseline as Record<string, unknown>)?.source as string}</div>
            <div><strong>{t('predictorProfile.domains')}:</strong> {((p.prediction_targets as Record<string, unknown>)?.target_domains as string[])?.join(', ')}</div>
            <div><strong>{t('predictorProfile.horizon')}:</strong> {(p.prediction_targets as Record<string, unknown>)?.time_horizon_months as number} mo</div>
          </div>
        </Card>
      ))}

      {!showForm && (
        <Button variant="primary" onClick={() => setShowForm(true)}>
          {t('predictorProfile.create')}
        </Button>
      )}

      {showForm && (
        <Card accent="blue">
          <h3 className="text-sm font-semibold mb-3">{t('predictorProfile.newProfile')}</h3>

          <div className="space-y-3">
            <div>
              <h4 className="text-xs font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>{t('predictorProfile.traitBaseline')}</h4>
              {TRAITS.map(trait => (
                <div key={trait} className="flex items-center gap-2 mb-1.5">
                  <label className="text-xs w-48" style={{ color: 'var(--color-text-secondary)' }}>{trait.replace(/_/g, ' ')}</label>
                  <Input
                    type="number"
                    min={0}
                    max={1}
                    step={0.1}
                    value={traits[trait] ?? ''}
                    onChange={e => setTraits({ ...traits, [trait]: e.target.value })}
                    placeholder="0.0–1.0"
                  />
                </div>
              ))}
              <Field label={t('predictorProfile.traitSource')}>
                <Select value={traitSource} onChange={e => setTraitSource(e.target.value as typeof traitSource)}>
                  <option value="short_self_report">short_self_report</option>
                  <option value="manual_estimate">manual_estimate</option>
                  <option value="unknown">unknown</option>
                </Select>
              </Field>
            </div>

            <div>
              <h4 className="text-xs font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>{t('predictorProfile.currentContext')}</h4>
              <Field label={t('predictorProfile.education')}>
                <Input value={context.education_status} onChange={e => setContext({ ...context, education_status: e.target.value })} />
              </Field>
              <Field label={t('predictorProfile.employment')}>
                <Input value={context.employment_status} onChange={e => setContext({ ...context, employment_status: e.target.value })} />
              </Field>
              <Field label={t('predictorProfile.financial')}>
                <Input value={context.financial_stability} onChange={e => setContext({ ...context, financial_stability: e.target.value })} />
              </Field>
              <Field label={t('predictorProfile.relationship')}>
                <Input value={context.relationship_status} onChange={e => setContext({ ...context, relationship_status: e.target.value })} />
              </Field>
              <Field label={t('predictorProfile.healthConstraints')}>
                <Input value={healthConstraints} onChange={e => setHealthConstraints(e.target.value)} placeholder={t('predictorProfile.commaList')} />
              </Field>
            </div>

            <div>
              <h4 className="text-xs font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>{t('predictorProfile.predictionTargets')}</h4>
              <div className="flex flex-wrap gap-1.5 mb-2">
                {DOMAINS.map(d => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => toggleDomain(d)}
                    className="px-2 py-1 rounded-full text-xs border-none cursor-pointer transition-colors"
                    style={{
                      backgroundColor: selectedDomains.includes(d) ? 'var(--color-accent)' : 'var(--color-surface)',
                      color: selectedDomains.includes(d) ? '#fff' : 'var(--color-text-secondary)',
                    }}
                  >
                    {d.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
              <Field label={t('predictorProfile.timeHorizon')}>
                <Input type="number" min={1} max={24} value={timeHorizon} onChange={e => setTimeHorizon(parseInt(e.target.value) || 6)} />
              </Field>
            </div>
          </div>

          <div className="flex gap-2 mt-3">
            <Button variant="primary" onClick={submit} disabled={createMutation.isPending}>
              {createMutation.isPending ? t('common.sending') : t('predictorProfile.save')}
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
