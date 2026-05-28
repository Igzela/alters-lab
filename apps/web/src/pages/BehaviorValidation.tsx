import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson, postJson } from '../api'
import { formatDate } from '../dateFormat'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Banner } from '../components/Banner'
import { Skeleton } from '../components/Skeleton'
import ErrorDisplay from '../components/ErrorDisplay'

interface BehaviorValidationRecord {
  validation_id: string
  outcome: string
  status: string
  weekly_review_count: number
  calibration_record_count: number
  pattern_review_count: number
  metrics: {
    action_alignment_score_improves: boolean
    repeated_negative_patterns_reduce: boolean
    primary_correction_completion_rate_improves: boolean
  }
  usage_integrity: {
    weekly_notes_completed_honestly: boolean
    calibration_records_created: boolean
    primary_corrections_set: boolean
    failure_reviews_honest: boolean
    self_deception_risk_not_softened: boolean
    sessions_not_skipped_too_often: boolean
  }
  usage_integrity_valid: boolean
  behavior_improved: boolean
  evidence_verified: boolean
  evidence_window_days: number | null
  message: string
  created_at: string
  p6_sealed: boolean
}

const OUTCOME_BADGE: Record<string, 'success' | 'warning' | 'error' | 'muted'> = {
  P6_BEHAVIOR_VALIDATED: 'success',
  P6_FAILED_TO_VALIDATE: 'warning',
  P6_USAGE_INVALID: 'error',
  P6_INSUFFICIENT_DATA: 'muted',
}

function CheckItem({ label, checked, yesLabel, noLabel }: { label: string; checked: boolean; yesLabel: string; noLabel: string }) {
  return (
    <div className="text-xs p-2 rounded-lg" style={{ backgroundColor: '#1a1c1a', border: '1px solid #242624' }}>
      <Badge variant={checked ? 'success' : 'error'}>{checked ? yesLabel : noLabel}</Badge>
      {' '}{label}
    </div>
  )
}

export default function BehaviorValidation() {
  const { t, i18n } = useTranslation()
  const [record, setRecord] = useState<BehaviorValidationRecord | null>(null)
  const [noReport, setNoReport] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const [loadingReport, setLoadingReport] = useState(true)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  const loadReport = useCallback(() => {
    setLoadingReport(true)
    setError('')
    fetchJson('/behavior-validation/report')
      .then(res => {
        if (res.status === 'no_report' || !res.validation) {
          setNoReport(true)
        } else {
          setRecord(res.validation)
        }
      })
      .catch(() => setNoReport(true))
      .finally(() => setLoadingReport(false))
  }, [])

  useEffect(() => { loadReport() }, [loadReport])

  const evaluate = async () => {
    setEvaluating(true)
    setError('')
    setStatus('')
    try {
      const res = await postJson('/behavior-validation/evaluate', {
        weekly_review_ids: [],
        calibration_record_ids: [],
        pattern_review_ids: [],
        metrics: {
          action_alignment_score_improves: false,
          repeated_negative_patterns_reduce: false,
          primary_correction_completion_rate_improves: false,
        },
        usage_integrity: {
          weekly_notes_completed_honestly: true,
          calibration_records_created: true,
          primary_corrections_set: false,
          failure_reviews_honest: true,
          self_deception_risk_not_softened: true,
          sessions_not_skipped_too_often: true,
        },
        save: true,
        caller: 'api',
      })
      setRecord(res.validation)
      setNoReport(false)
      setStatus(`${t('validation.evalComplete')} ${res.validation.outcome}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('validation.evalFailed'))
    } finally {
      setEvaluating(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('validation.title')}</h2>
      <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('validation.description')}</p>

      <Banner variant="warning">
        <strong>{t('validation.p6Status')}</strong>
        <p className="text-xs mt-1" style={{ color: '#7c7c6f' }}>{t('validation.p6Remains')}</p>
      </Banner>

      <div className="flex items-center gap-3 mb-4">
        <Button variant="primary" accent="orange" onClick={evaluate} disabled={evaluating}>
          {evaluating ? t('validation.evaluating') : t('validation.runEvaluation')}
        </Button>
        {status && <span className="text-sm" style={{ color: '#0ae448' }}>{status}</span>}
        {error && <Banner variant="error">{error}</Banner>}
      </div>

      {loadingReport && <Skeleton lines={4} />}

      {!loadingReport && noReport && !record && (
        <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('validation.noReport')}</p>
      )}

      {record && (
        <Card accent="orange">
          <h3 className="text-sm font-medium mb-3">{t('validation.validationReport')}</h3>

          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 mb-3">
            <div>
              <Badge variant={OUTCOME_BADGE[record.outcome] || 'muted'}>
                {record.outcome.replace(/_/g, ' ')}
              </Badge>
            </div>
            <div className="text-sm"><strong>{record.weekly_review_count}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('validation.weeklyReviews')}</span></div>
            <div className="text-sm"><strong>{record.calibration_record_count}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('validation.calibrationRecords')}</span></div>
            <div className="text-sm"><strong>{record.pattern_review_count}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('validation.patternReviews')}</span></div>
            {record.evidence_window_days != null && (
              <div className="text-sm"><strong>{record.evidence_window_days}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('validation.evidenceWindow')}</span></div>
            )}
          </div>

          <div className="p-2.5 rounded-lg mb-3" style={{ backgroundColor: '#1a1c1a', border: '1px solid #242624' }}>
            <p className="text-sm">{record.message}</p>
          </div>

          <h4 className="text-sm font-medium mb-2">{t('validation.metrics')}</h4>
          <div className="grid grid-cols-3 gap-2 mb-3">
            <CheckItem label={t('validation.alignmentImproves')} checked={record.metrics.action_alignment_score_improves} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
            <CheckItem label={t('validation.patternsReduce')} checked={record.metrics.repeated_negative_patterns_reduce} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
            <CheckItem label={t('validation.correctionImproves')} checked={record.metrics.primary_correction_completion_rate_improves} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
          </div>

          <h4 className="text-sm font-medium mb-2">{t('validation.usageIntegrity')}</h4>
          <div className="grid grid-cols-2 gap-2 mb-3">
            <CheckItem label={t('validation.weeklyNotesHonest')} checked={record.usage_integrity.weekly_notes_completed_honestly} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
            <CheckItem label={t('validation.calibrationCreated')} checked={record.usage_integrity.calibration_records_created} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
            <CheckItem label={t('validation.correctionsSet')} checked={record.usage_integrity.primary_corrections_set} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
            <CheckItem label={t('validation.failureHonest')} checked={record.usage_integrity.failure_reviews_honest} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
            <CheckItem label={t('validation.selfDeception')} checked={record.usage_integrity.self_deception_risk_not_softened} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
            <CheckItem label={t('validation.sessionsNotSkipped')} checked={record.usage_integrity.sessions_not_skipped_too_often} yesLabel={t('validation.yes')} noLabel={t('validation.no')} />
          </div>

          <div className="grid grid-cols-3 gap-2.5 text-xs" style={{ color: '#c4c2b8' }}>
            <div>{t('validation.integrityValid')} <strong>{record.usage_integrity_valid ? t('validation.yes') : t('validation.no')}</strong></div>
            <div>{t('validation.behaviorImproved')} <strong>{record.behavior_improved ? t('validation.yes') : t('validation.no')}</strong></div>
            <div>{t('validation.evidenceVerified')} <strong>{record.evidence_verified ? t('validation.yes') : t('validation.no')}</strong></div>
          </div>

          {record.created_at && (
            <p className="text-xs mt-2" style={{ color: '#7c7c6f' }}>{t('validation.evaluated')} {formatDate(record.created_at, i18n.language)}</p>
          )}
        </Card>
      )}
    </div>
  )
}
