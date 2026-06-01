import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  useForecastSnapshots,
  useExternalEvidence,
  useCreateExternalEvidence,
  useForecastEvaluations,
  useCreateForecastEvaluation,
  useForecastScorecard,
} from '../hooks/useForecastHooks'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { Field, Input, Select, TextArea } from '../components/Input'
import ErrorDisplay from '../components/ErrorDisplay'
import { Skeleton } from '../components/Skeleton'

type Tab = 'snapshots' | 'evidence' | 'evaluations' | 'scorecard'

const STRENGTH_COLORS: Record<string, 'success' | 'warning' | 'error' | 'muted'> = {
  strong: 'success',
  moderate: 'warning',
  weak: 'error',
}

const MATCH_COLORS: Record<string, 'success' | 'error' | 'warning' | 'info' | 'muted'> = {
  hit: 'success',
  miss: 'error',
  partial: 'warning',
  unknown: 'muted',
}

const CONFIDENCE_COLORS: Record<string, 'success' | 'warning' | 'error' | 'muted'> = {
  high: 'success',
  medium: 'warning',
  low: 'error',
}

export default function ForecastCalibration() {
  const { t } = useTranslation()
  const [tab, setTab] = useState<Tab>('snapshots')

  const tabs: { key: Tab; label: string }[] = [
    { key: 'snapshots', label: t('forecastCalibration.tabs.snapshots') },
    { key: 'evidence', label: t('forecastCalibration.tabs.evidence') },
    { key: 'evaluations', label: t('forecastCalibration.tabs.evaluations') },
    { key: 'scorecard', label: t('forecastCalibration.tabs.scorecard') },
  ]

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('forecastCalibration.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('forecastCalibration.description')}</p>

      <div className="flex gap-1 border-b" style={{ borderColor: 'var(--color-border)' }}>
        {tabs.map(tb => (
          <button
            key={tb.key}
            onClick={() => setTab(tb.key)}
            className="px-3 py-1.5 text-sm font-medium transition-colors border-b-2 -mb-px"
            style={{
              color: tab === tb.key ? 'var(--color-accent)' : 'var(--color-text-secondary)',
              borderColor: tab === tb.key ? 'var(--color-accent)' : 'transparent',
            }}
          >
            {tb.label}
          </button>
        ))}
      </div>

      {tab === 'snapshots' && <SnapshotsTab />}
      {tab === 'evidence' && <EvidenceTab />}
      {tab === 'evaluations' && <EvaluationsTab />}
      {tab === 'scorecard' && <ScorecardTab />}
    </div>
  )
}

function SnapshotsTab() {
  const { t } = useTranslation()
  const { data, isLoading, error } = useForecastSnapshots()

  if (isLoading) return <Skeleton lines={4} />
  if (error) return <ErrorDisplay message={(error as Error).message} />

  const snapshots: Record<string, unknown>[] = (data as Record<string, unknown> | undefined)?.snapshots as Record<string, unknown>[] || []

  if (snapshots.length === 0) {
    return <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>{t('forecastCalibration.noSnapshots')}</p>
  }

  return (
    <div className="space-y-3">
      {snapshots.map((snap, i) => (
        <Card key={i} accent="amber">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">{snap.branch_id as string}</span>
              <Badge variant="muted">{snap.snapshot_id as string}</Badge>
              {Boolean(snap.locked) && <Badge variant="info">locked</Badge>}
            </div>
            <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
              {snap.created_at as string}
            </span>
          </div>

          <div className="flex gap-4 text-xs mb-2" style={{ color: 'var(--color-text-secondary)' }}>
            <span>{t('forecastCalibration.horizon')}: {snap.horizon_months as number}mo</span>
            {(() => {
              const summary = snap.forecast_summary as Record<string, unknown> | undefined
              if (!summary) return null
              return (
                <>
                  <span className="flex items-center gap-1">
                    {t('forecastCalibration.direction')}:
                    <Badge variant={MATCH_COLORS[summary.trajectory_direction as string] || 'muted'}>
                      {summary.trajectory_direction as string}
                    </Badge>
                  </span>
                  <span className="flex items-center gap-1">
                    {t('forecastCalibration.confidence')}:
                    <Badge variant={CONFIDENCE_COLORS[summary.confidence as string] || 'muted'}>
                      {summary.confidence as string}
                    </Badge>
                  </span>
                </>
              )
            })()}
          </div>

          {/* Domain Predictions */}
          {(() => {
            const preds = snap.domain_predictions as Record<string, unknown>[] | undefined
            if (!preds || preds.length === 0) return null
            return (
              <div className="mt-2">
                <h4 className="text-xs font-semibold mb-1">{t('forecastCalibration.domainPredictions')}</h4>
                <div className="space-y-1">
                  {preds.map((dp, j) => (
                    <div key={j} className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                      <span className="w-28">{dp.domain as string}</span>
                      <Badge variant={MATCH_COLORS[dp.predicted_direction as string] || 'muted'}>
                        {dp.predicted_direction as string}
                      </Badge>
                      <span className="text-[10px]" style={{ color: 'var(--color-text-muted)' }}>
                        ({dp.source as string})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })()}

          {/* Limitations */}
          {(() => {
            const lims = snap.limitations as string[] | undefined
            if (!lims || lims.length === 0) return null
            return (
              <div className="mt-2">
                <h4 className="text-xs font-semibold mb-1">{t('forecastCalibration.limitations')}</h4>
                <ul className="text-xs space-y-0.5" style={{ color: 'var(--color-text-muted)' }}>
                  {lims.map((lim, k) => <li key={k}>• {lim}</li>)}
                </ul>
              </div>
            )
          })()}
        </Card>
      ))}
    </div>
  )
}

function EvidenceTab() {
  const { t } = useTranslation()
  const { data, isLoading, error } = useExternalEvidence()
  const createMutation = useCreateExternalEvidence()

  const [domain, setDomain] = useState('career_education')
  const [evidenceType, setEvidenceType] = useState('other')
  const [description, setDescription] = useState('')
  const [strength, setStrength] = useState('moderate')
  const [polarity, setPolarity] = useState('positive')
  const [branchId, setBranchId] = useState('')

  if (isLoading) return <Skeleton lines={4} />
  if (error) return <ErrorDisplay message={(error as Error).message} />

  const evidence: Record<string, unknown>[] = (data as Record<string, unknown> | undefined)?.evidence as Record<string, unknown>[] || []

  const handleCreate = () => {
    const body: Record<string, unknown> = {
      domain,
      evidence_type: evidenceType,
      description,
      objective_strength: strength,
      polarity,
    }
    if (branchId) body.branch_id = branchId
    createMutation.mutate(body, {
      onSuccess: () => {
        setDescription('')
        setBranchId('')
      },
    })
  }

  return (
    <div className="space-y-3">
      <Card>
        <h3 className="text-sm font-semibold mb-2">{t('forecastCalibration.addEvidence')}</h3>
        <div className="space-y-2">
          <div className="flex gap-2">
            <Field label={t('forecastCalibration.domain')}>
              <Select value={domain} onChange={e => setDomain(e.target.value)}>
                <option value="career_education">career_education</option>
                <option value="financial">financial</option>
                <option value="health">health</option>
                <option value="relationship">relationship</option>
                <option value="subjective_wellbeing">subjective_wellbeing</option>
              </Select>
            </Field>
            <Field label={t('forecastCalibration.evidenceType')}>
              <Select value={evidenceType} onChange={e => setEvidenceType(e.target.value)}>
                <option value="milestone_completed">milestone_completed</option>
                <option value="exam_or_certification">exam_or_certification</option>
                <option value="job_or_market_feedback">job_or_market_feedback</option>
                <option value="project_shipped">project_shipped</option>
                <option value="income_or_financial_change">income_or_financial_change</option>
                <option value="health_measurement">health_measurement</option>
                <option value="relationship_event">relationship_event</option>
                <option value="user_or_customer_feedback">user_or_customer_feedback</option>
                <option value="other">other</option>
              </Select>
            </Field>
          </div>
          <Field label={t('forecastCalibration.description')}>
            <TextArea value={description} onChange={e => setDescription(e.target.value)} rows={2} />
          </Field>
          <div className="flex gap-2">
            <Field label={t('forecastCalibration.strength')}>
              <Select value={strength} onChange={e => setStrength(e.target.value)}>
                <option value="weak">weak</option>
                <option value="moderate">moderate</option>
                <option value="strong">strong</option>
              </Select>
            </Field>
            <Field label={t('forecastCalibration.polarity')}>
              <Select value={polarity} onChange={e => setPolarity(e.target.value)}>
                <option value="positive">positive</option>
                <option value="negative">negative</option>
                <option value="neutral">neutral</option>
                <option value="mixed">mixed</option>
              </Select>
            </Field>
            <Field label={t('forecastCalibration.branchId')}>
              <Input value={branchId} onChange={e => setBranchId(e.target.value)} placeholder="branch_A" />
            </Field>
          </div>
          <Button variant="primary" onClick={handleCreate} disabled={createMutation.isPending || !description}>
            {createMutation.isPending ? t('common.saving') : t('forecastCalibration.submitEvidence')}
          </Button>
          {createMutation.error && <ErrorDisplay message={(createMutation.error as Error).message} />}
        </div>
      </Card>

      {evidence.length === 0 ? (
        <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>{t('forecastCalibration.noEvidence')}</p>
      ) : (
        evidence.map((ev, i) => (
          <Card key={i}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono">{ev.domain as string}</span>
                <Badge variant="muted">{ev.evidence_type as string}</Badge>
                <Badge variant={STRENGTH_COLORS[ev.objective_strength as string] || 'muted'}>
                  {ev.objective_strength as string}
                </Badge>
              </div>
              <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{ev.observed_at as string}</span>
            </div>
            <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{ev.description as string}</p>
          </Card>
        ))
      )}
    </div>
  )
}

function EvaluationsTab() {
  const { t } = useTranslation()
  const { data, isLoading, error } = useForecastEvaluations()
  const createMutation = useCreateForecastEvaluation()
  const snapshotsQuery = useForecastSnapshots()
  const evidenceQuery = useExternalEvidence()

  const [snapshotId, setSnapshotId] = useState('')
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([])

  if (isLoading || snapshotsQuery.isLoading) return <Skeleton lines={4} />
  if (error) return <ErrorDisplay message={(error as Error).message} />

  const evaluations: Record<string, unknown>[] = (data as Record<string, unknown> | undefined)?.evaluations as Record<string, unknown>[] || []
  const snapshots: Record<string, unknown>[] = (snapshotsQuery.data as Record<string, unknown> | undefined)?.snapshots as Record<string, unknown>[] || []
  const evidence: Record<string, unknown>[] = (evidenceQuery.data as Record<string, unknown> | undefined)?.evidence as Record<string, unknown>[] || []

  const toggleEvidence = (eid: string) => {
    setSelectedEvidence(prev =>
      prev.includes(eid) ? prev.filter(x => x !== eid) : [...prev, eid]
    )
  }

  const handleEvaluate = () => {
    createMutation.mutate({
      snapshot_id: snapshotId,
      evidence_ids: selectedEvidence,
    })
  }

  return (
    <div className="space-y-3">
      <Card>
        <h3 className="text-sm font-semibold mb-2">{t('forecastCalibration.runEvaluation')}</h3>
        <div className="space-y-2">
          <Field label={t('forecastCalibration.snapshot')}>
            <Select value={snapshotId} onChange={e => setSnapshotId(e.target.value)}>
              <option value="">{t('forecastCalibration.selectSnapshot')}</option>
              {snapshots.map(s => (
                <option key={s.snapshot_id as string} value={s.snapshot_id as string}>
                  {s.snapshot_id as string} — {s.branch_id as string}
                </option>
              ))}
            </Select>
          </Field>

          {evidence.length > 0 && (
            <div>
              <label className="text-xs font-medium block mb-1">{t('forecastCalibration.selectEvidence')}</label>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {evidence.map(ev => (
                  <label key={ev.evidence_id as string} className="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedEvidence.includes(ev.evidence_id as string)}
                      onChange={() => toggleEvidence(ev.evidence_id as string)}
                    />
                    <span className="font-mono">{ev.domain as string}</span>
                    <span style={{ color: 'var(--color-text-secondary)' }}>{ev.description as string}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <Button variant="primary" onClick={handleEvaluate} disabled={createMutation.isPending || !snapshotId}>
            {createMutation.isPending ? t('common.generating') : t('forecastCalibration.evaluate')}
          </Button>
          {createMutation.error && <ErrorDisplay message={(createMutation.error as Error).message} />}
        </div>
      </Card>

      {evaluations.length === 0 ? (
        <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>{t('forecastCalibration.noEvaluations')}</p>
      ) : (
        evaluations.map((ev, i) => (
          <Card key={i} accent="green">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Badge variant={ev.evaluation_type === 'final' ? 'success' : 'warning'}>
                  {ev.evaluation_type as string}
                </Badge>
                <Badge variant={MATCH_COLORS[ev.overall_result as string] || 'muted'}>
                  {ev.overall_result as string}
                </Badge>
              </div>
              <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{ev.evaluated_at as string}</span>
            </div>

            {ev.days_until_due != null && (
              <p className="text-xs mb-2" style={{ color: 'var(--color-text-secondary)' }}>
                {t('forecastCalibration.daysUntilDue')}: {ev.days_until_due as number}
              </p>
            )}

            {/* Domain Results */}
            {(() => {
              const drs = ev.domain_results as Record<string, unknown>[] | undefined
              if (!drs || drs.length === 0) return null
              return (
                <div className="mt-2">
                  <h4 className="text-xs font-semibold mb-1">{t('forecastCalibration.domainResults')}</h4>
                  <div className="space-y-1">
                    {drs.map((dr, j) => (
                      <div key={j} className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                        <span className="w-28">{dr.domain as string}</span>
                        <span>{dr.predicted_direction as string}</span>
                        <span style={{ color: 'var(--color-text-muted)' }}>({dr.predicted_direction_source as string})</span>
                        <span>→</span>
                        <span>{dr.observed_direction as string}</span>
                        <Badge variant={MATCH_COLORS[dr.match_result as string] || 'muted'}>
                          {dr.match_result as string}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })()}

            {/* Signals */}
            {(() => {
              const ps = ev.predictive_signals as string[] | undefined
              const ms = ev.misleading_signals as string[] | undefined
              if ((!ps || ps.length === 0) && (!ms || ms.length === 0)) return null
              return (
                <div className="mt-2 space-y-1">
                  {ps && ps.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-green-600">{t('forecastCalibration.predictiveSignals')}</h4>
                      {ps.map((s, k) => <p key={k} className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>✓ {s}</p>)}
                    </div>
                  )}
                  {ms && ms.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-red-600">{t('forecastCalibration.misleadingSignals')}</h4>
                      {ms.map((s, k) => <p key={k} className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>✗ {s}</p>)}
                    </div>
                  )}
                </div>
              )
            })()}

            {/* Limitations */}
            {(() => {
              const lims = ev.limitations as string[] | undefined
              if (!lims || lims.length === 0) return null
              return (
                <div className="mt-2">
                  <h4 className="text-xs font-semibold mb-1">{t('forecastCalibration.limitations')}</h4>
                  <ul className="text-xs space-y-0.5" style={{ color: 'var(--color-text-muted)' }}>
                    {lims.map((lim, k) => <li key={k}>• {lim}</li>)}
                  </ul>
                </div>
              )
            })()}
          </Card>
        ))
      )}
    </div>
  )
}

function ScorecardTab() {
  const { t } = useTranslation()
  const { data, isLoading, error } = useForecastScorecard()

  if (isLoading) return <Skeleton lines={4} />
  if (error) return <ErrorDisplay message={(error as Error).message} />

  const scorecard = data as Record<string, unknown> | undefined
  if (!scorecard) return null

  const total = scorecard.total_evaluations as number
  const sampleTooSmall = total < 5

  return (
    <div className="space-y-3">
      <Card accent="amber">
        <h3 className="text-sm font-semibold mb-2">{t('forecastCalibration.overallResults')}</h3>
        <div className="flex gap-4 text-sm">
          <div><span className="font-mono">{total}</span> {t('forecastCalibration.total')}</div>
          <div><Badge variant="success">{scorecard.hit_count as number}</Badge> {t('forecastCalibration.hits')}</div>
          <div><Badge variant="error">{scorecard.miss_count as number}</Badge> {t('forecastCalibration.misses')}</div>
          <div><Badge variant="warning">{scorecard.partial_count as number}</Badge> {t('forecastCalibration.partial')}</div>
          <div><Badge variant="muted">{scorecard.unknown_count as number}</Badge> {t('forecastCalibration.unknown')}</div>
        </div>
      </Card>

      {sampleTooSmall && (
        <Card accent="amber">
          <p className="text-xs" style={{ color: 'var(--color-accent)' }}>
            ⚠ {t('forecastCalibration.sampleSizeWarning', { count: total })}
          </p>
        </Card>
      )}

      <Card>
        <h3 className="text-sm font-semibold mb-2">{t('forecastCalibration.calibrationConfidence')}</h3>
        <Badge variant={CONFIDENCE_COLORS[scorecard.calibration_confidence as string] || 'muted'}>
          {scorecard.calibration_confidence as string}
        </Badge>
        {sampleTooSmall && (
          <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
            {t('forecastCalibration.confidenceNote')}
          </p>
        )}
      </Card>

      {/* By Domain */}
      {(() => {
        const domains = scorecard.by_domain as Record<string, unknown>[] | undefined
        if (!domains || domains.length === 0) return null
        return (
          <Card>
            <h3 className="text-sm font-semibold mb-2">{t('forecastCalibration.byDomain')}</h3>
            <div className="space-y-2">
              {domains.map((d, i) => (
                <div key={i} className="flex items-center gap-3 text-xs">
                  <span className="w-28">{d.domain as string}</span>
                  <span style={{ color: 'var(--color-text-secondary)' }}>
                    {t('forecastCalibration.hitRate')}: {d.hit_rate != null ? `${((d.hit_rate as number) * 100).toFixed(0)}%` : '—'}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )
      })()}

      {/* Signal Quality */}
      {(() => {
        const sq = scorecard.signal_quality as Record<string, unknown> | undefined
        if (!sq) return null
        const ps = sq.predictive_signals as string[] || []
        const ms = sq.misleading_signals as string[] || []
        if (ps.length === 0 && ms.length === 0) return null
        return (
          <Card>
            <h3 className="text-sm font-semibold mb-2">{t('forecastCalibration.signalQuality')}</h3>
            {ps.length > 0 && (
              <div className="mb-2">
                <h4 className="text-xs font-semibold text-green-600">{t('forecastCalibration.predictiveSignals')}</h4>
                {ps.map((s, i) => <p key={i} className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>✓ {s}</p>)}
              </div>
            )}
            {ms.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-red-600">{t('forecastCalibration.misleadingSignals')}</h4>
                {ms.map((s, i) => <p key={i} className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>✗ {s}</p>)}
              </div>
            )}
          </Card>
        )
      })()}

      {/* Limitations */}
      {(() => {
        const lims = scorecard.limitations as string[] | undefined
        if (!lims || lims.length === 0) return null
        return (
          <Card>
            <h3 className="text-sm font-semibold mb-2">{t('forecastCalibration.limitations')}</h3>
            <ul className="text-xs space-y-0.5" style={{ color: 'var(--color-text-muted)' }}>
              {lims.map((lim, i) => <li key={i}>• {lim}</li>)}
            </ul>
          </Card>
        )
      })()}
    </div>
  )
}
