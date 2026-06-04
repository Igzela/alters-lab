import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useBranchForecast, useCalibrationDivergence, usePredictorProfiles } from '../hooks/usePredictionHooks'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Field, Input, Select } from '../components/Input'
import { Banner } from '../components/Banner'
import { Badge } from '../components/Badge'
import ErrorDisplay from '../components/ErrorDisplay'

const DIRECTION_COLORS: Record<string, 'success' | 'error' | 'warning' | 'info' | 'muted'> = {
  improving: 'success',
  declining: 'error',
  stable: 'info',
  mixed: 'warning',
  unknown: 'muted',
  favorable: 'success',
  unfavorable: 'error',
}

export default function BranchForecast() {
  const { t } = useTranslation()
  const forecastMutation = useBranchForecast()
  const divergenceMutation = useCalibrationDivergence()
  const profilesQuery = usePredictorProfiles()

  const [branchId, setBranchId] = useState('')
  const [profileId, setProfileId] = useState('')
  const [lookbackWeeks, setLookbackWeeks] = useState(8)
  const [horizonMonths, setHorizonMonths] = useState(3)

  const profiles: Record<string, unknown>[] = (profilesQuery.data as Record<string, unknown> | undefined)?.profiles as Record<string, unknown>[] || []
  const forecast = forecastMutation.data as Record<string, unknown> | undefined
  const divergence = divergenceMutation.data as Record<string, unknown> | undefined

  const runForecast = () => {
    const body: Record<string, unknown> = { branch_id: branchId, lookback_weeks: lookbackWeeks, horizon_months: horizonMonths }
    if (profileId) body.profile_id = profileId
    forecastMutation.mutate(body)
    divergenceMutation.mutate({ branch_id: branchId || undefined, lookback_weeks: lookbackWeeks })
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('branchForecast.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('branchForecast.description')}</p>

      <Card>
        <div className="space-y-3">
          <Field label={t('branchForecast.branchId')}>
            <Input value={branchId} onChange={e => setBranchId(e.target.value)} placeholder="branch_A" />
          </Field>
          <Field label={t('branchForecast.profile')}>
            <Select value={profileId} onChange={e => setProfileId(e.target.value)}>
              <option value="">{t('branchForecast.noProfile')}</option>
              {profiles.map(p => (
                <option key={p.profile_id as string} value={p.profile_id as string}>{p.profile_id as string}</option>
              ))}
            </Select>
          </Field>
          <div className="flex gap-3">
            <Field label={t('branchForecast.lookback')}>
              <Input type="number" min={2} max={52} value={lookbackWeeks} onChange={e => setLookbackWeeks(parseInt(e.target.value) || 8)} />
            </Field>
            <Field label={t('branchForecast.horizon')}>
              <Input type="number" min={1} max={24} value={horizonMonths} onChange={e => setHorizonMonths(parseInt(e.target.value) || 3)} />
            </Field>
          </div>
          <Button variant="primary" onClick={runForecast} disabled={forecastMutation.isPending || !branchId}>
            {forecastMutation.isPending ? t('common.generating') : t('branchForecast.analyze')}
          </Button>
        </div>
      </Card>

      {forecastMutation.error && <ErrorDisplay message={(forecastMutation.error as Error).message} />}
      {divergenceMutation.error && <ErrorDisplay message={(divergenceMutation.error as Error).message} />}

      {forecast && (
        <>
          {/* Forecast Summary */}
          <Card accent="amber">
            <h3 className="text-sm font-semibold mb-2">{t('branchForecast.forecastSummary')}</h3>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <span style={{ color: 'var(--color-text-secondary)' }}>{t('branchForecast.trajectory')}:</span>
                <Badge variant={DIRECTION_COLORS[(forecast.forecast_summary as Record<string, unknown>)?.trajectory_direction as string] || 'muted'}>
                  {(forecast.forecast_summary as Record<string, unknown>)?.trajectory_direction as string}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span style={{ color: 'var(--color-text-secondary)' }}>{t('branchForecast.confidence')}:</span>
                <span>{(forecast.forecast_summary as Record<string, unknown>)?.confidence as string}</span>
              </div>
              <div className="flex items-center gap-2">
                <span style={{ color: 'var(--color-text-secondary)' }}>{t('branchForecast.credibility')}:</span>
                <span>{(forecast.forecast_summary as Record<string, unknown>)?.credibility as string}</span>
              </div>
              <p className="mt-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                {(forecast.forecast_summary as Record<string, unknown>)?.explanation as string}
              </p>
            </div>
          </Card>

          {/* Route A: Personal Evidence */}
          <Card accent="green">
            <h3 className="text-sm font-semibold mb-2">{t('branchForecast.routeA')}</h3>
            {(() => {
              const routeA = forecast.route_a_personal_evidence as Record<string, unknown>
              if (!routeA?.available) {
                return <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{t('branchForecast.routeAUnavailable')}</p>
              }
              return (
                <div className="space-y-1 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                  <div><strong>{t('branchForecast.behaviorTrends')}:</strong> {routeA.behavior_trends_summary as string}</div>
                  <div><strong>{t('branchForecast.milestoneProgress')}:</strong> {routeA.milestone_progress_summary as string}</div>
                  <div><strong>{t('branchForecast.actionAlignment')}:</strong> {routeA.action_alignment_summary as string}</div>
                </div>
              )
            })()}
          </Card>

          {/* Route B: Population Prior */}
          <Card accent="blue">
            <h3 className="text-sm font-semibold mb-2">{t('branchForecast.routeB')}</h3>
            {(() => {
              const routeB = forecast.route_b_population_prior as Record<string, unknown>
              if (!routeB?.available) {
                return <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{t('branchForecast.routeBUnavailable')}</p>
              }
              const artifactClass = routeB.artifact_class as string
              const strengthLevel = routeB.strength_level as string
              const classBadge = strengthLevel === 'strong_calibrated'
                ? { variant: 'success' as const, label: 'Strong Calibrated Public Model' }
                : strengthLevel === 'data_backed'
                  ? { variant: 'warning' as const, label: 'Data-Backed Descriptive Baseline' }
                  : strengthLevel === 'contextual'
                    ? { variant: 'muted' as const, label: 'Contextual Literature Prior' }
                    : artifactClass === 'mixed'
                      ? { variant: 'warning' as const, label: 'Mixed (Data + Contextual)' }
                      : { variant: 'muted' as const, label: 'No Route B Prior' }
              const calibrationMetrics = routeB.calibration_metrics as Record<string, unknown> | undefined
              return (
                <div className="space-y-1 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={classBadge.variant}>
                      {classBadge.label}
                    </Badge>
                    {strengthLevel !== 'strong_calibrated' && strengthLevel !== 'data_backed' && strengthLevel !== 'none' && (
                      <span style={{ color: 'var(--color-error)' }}>— Route B not fully approved for this forecast</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span>{t('branchForecast.priorDirection')}:</span>
                    <Badge variant={DIRECTION_COLORS[routeB.prior_direction as string] || 'muted'}>{routeB.prior_direction as string}</Badge>
                  </div>
                  <div><strong>{t('branchForecast.transferRisk')}:</strong> {routeB.transfer_risk as string}</div>
                  <div><strong>{t('branchForecast.evidenceStrength')}:</strong> {routeB.evidence_strength as string}</div>
                  <div><strong>Approved Artifacts:</strong> {routeB.approved_artifact_count as number}</div>
                  {(routeB.contextual_prior_ids as string[] || []).length > 0 && (
                    <div><strong>Contextual Priors:</strong> {(routeB.contextual_prior_ids as string[]).join(', ')} (not driving forecast)</div>
                  )}
                  <p className="mt-1">{routeB.explanation as string}</p>
                  {calibrationMetrics && Object.values(calibrationMetrics).some(v => v != null) && (
                    <div className="mt-2 p-2 rounded" style={{
                      backgroundColor: strengthLevel === 'strong_calibrated' ? 'var(--color-accent-bg)' : 'var(--color-surface)',
                      border: strengthLevel === 'strong_calibrated' ? '1px solid var(--color-accent)' : '1px solid var(--color-border)',
                    }}>
                      <div className="font-medium mb-1">Model Performance</div>
                      <div className="flex gap-4 flex-wrap">
                        {calibrationMetrics.brier_score != null && (
                          <span className="font-mono">Brier: {Number(calibrationMetrics.brier_score).toFixed(3)}</span>
                        )}
                        {calibrationMetrics.calibration_slope != null && (
                          <span className="font-mono">Slope: {Number(calibrationMetrics.calibration_slope).toFixed(3)}</span>
                        )}
                        {calibrationMetrics.auc != null && (
                          <span className="font-mono">AUC: {Number(calibrationMetrics.auc).toFixed(3)}</span>
                        )}
                        {calibrationMetrics.r2 != null && (
                          <span className="font-mono">R²: {Number(calibrationMetrics.r2).toFixed(3)}</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )
            })()}
          </Card>

          {/* Calibration Divergence */}
          <Card accent="amber">
            <h3 className="text-sm font-semibold mb-2">{t('branchForecast.calibrationDivergence')}</h3>
            {(() => {
              const calDiv = forecast.calibration_divergence as Record<string, unknown>
              return (
                <div className="space-y-1 text-xs">
                  <div className="flex items-center gap-2">
                    <span style={{ color: 'var(--color-text-secondary)' }}>{t('branchForecast.status')}:</span>
                    <Badge variant={calDiv.divergence_status === 'converging' ? 'success' : calDiv.divergence_status === 'mixed' ? 'warning' : 'error'}>
                      {calDiv.divergence_status as string}
                    </Badge>
                  </div>
                  {(calDiv.flags as Record<string, unknown>[] || []).map((flag, i) => (
                    <div key={i} className="mt-1 p-2 rounded" style={{ backgroundColor: 'var(--color-surface)' }}>
                      <Badge variant={flag.severity === 'critical' ? 'error' : flag.severity === 'warn' ? 'warning' : 'info'}>
                        {flag.severity as string}
                      </Badge>
                      <p className="mt-1" style={{ color: 'var(--color-text-secondary)' }}>{flag.explanation as string}</p>
                    </div>
                  ))}
                </div>
              )
            })()}
          </Card>

          {/* Outcome Targets Summary */}
          <Card>
            <h3 className="text-sm font-semibold mb-2">{t('branchForecast.outcomeTargets')}</h3>
            {(() => {
              const ot = forecast.outcome_targets as Record<string, unknown>
              return (
                <div className="flex gap-4 text-sm">
                  <div><span className="font-mono">{ot.active_targets as number}</span> {t('branchForecast.active')}</div>
                  <div><span className="font-mono">{ot.achieved_targets as number}</span> {t('branchForecast.achieved')}</div>
                  <div><span className="font-mono">{ot.missed_targets as number}</span> {t('branchForecast.missed')}</div>
                </div>
              )
            })()}
          </Card>

          {/* Limitations */}
          <Card>
            <h3 className="text-sm font-semibold mb-2">{t('branchForecast.limitations')}</h3>
            <ul className="text-xs space-y-1" style={{ color: 'var(--color-text-secondary)' }}>
              {(forecast.limitations as string[] || []).map((lim, i) => (
                <li key={i} className="flex gap-1.5">
                  <span style={{ color: 'var(--color-text-muted)' }}>•</span>
                  {lim}
                </li>
              ))}
            </ul>
          </Card>

          {/* Next Evidence to Collect */}
          <Card>
            <h3 className="text-sm font-semibold mb-2">{t('branchForecast.nextEvidence')}</h3>
            <ul className="text-xs space-y-1" style={{ color: 'var(--color-text-secondary)' }}>
              {(forecast.next_evidence_to_collect as string[] || []).map((item, i) => (
                <li key={i} className="flex gap-1.5">
                  <span style={{ color: 'var(--color-accent)' }}>→</span>
                  {item}
                </li>
              ))}
            </ul>
          </Card>
        </>
      )}

      {/* Standalone Calibration Divergence result (if run separately) */}
      {divergence && !forecast && (
        <Card accent="amber">
          <h3 className="text-sm font-semibold mb-2">{t('branchForecast.calibrationDivergence')}</h3>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <span style={{ color: 'var(--color-text-secondary)' }}>{t('branchForecast.status')}:</span>
              <Badge variant={divergence.divergence_status === 'converging' ? 'success' : divergence.divergence_status === 'mixed' ? 'warning' : 'error'}>
                {divergence.divergence_status as string}
              </Badge>
            </div>
            {(divergence.flags as Record<string, unknown>[] || []).map((flag, i) => (
              <div key={i} className="mt-1 p-2 rounded" style={{ backgroundColor: 'var(--color-surface)' }}>
                <Badge variant={flag.severity === 'critical' ? 'error' : flag.severity === 'warn' ? 'warning' : 'info'}>
                  {flag.severity as string}
                </Badge>
                <p className="mt-1" style={{ color: 'var(--color-text-secondary)' }}>{flag.explanation as string}</p>
                {flag.suggested_calibration_question != null && (
                  <p className="mt-1 italic" style={{ color: 'var(--color-accent)' }}>{String(flag.suggested_calibration_question)}</p>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
