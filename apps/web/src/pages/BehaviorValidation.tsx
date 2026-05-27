import { useState, useEffect } from 'react'
import { fetchJson, postJson } from '../api'

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

const OUTCOME_COLORS: Record<string, string> = {
  P6_BEHAVIOR_VALIDATED: '#4caf50',
  P6_FAILED_TO_VALIDATE: '#e65100',
  P6_USAGE_INVALID: '#b00020',
  P6_INSUFFICIENT_DATA: '#888',
}

export default function BehaviorValidation() {
  const [record, setRecord] = useState<BehaviorValidationRecord | null>(null)
  const [noReport, setNoReport] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  useEffect(() => {
    fetchJson('/behavior-validation/report')
      .then(res => {
        if (res.status === 'no_report' || !res.validation) {
          setNoReport(true)
        } else {
          setRecord(res.validation)
        }
      })
      .catch(() => setNoReport(true))
  }, [])

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
      setStatus(`Evaluation complete: ${res.validation.outcome}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Evaluation failed')
    } finally {
      setEvaluating(false)
    }
  }

  return (
    <div>
      <h2>Behavior Validation</h2>
      <p style={{ color: '#888', fontSize: 12 }}>
        Evaluates whether your behavior has improved based on weekly reviews, calibration records, and pattern reviews. This does NOT automatically validate P6 — validation requires explicit human approval.
      </p>

      <div style={{ padding: 12, background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: 6, marginBottom: 16 }}>
        <strong>P6 validation status: Not started.</strong> This page shows evaluation results only. P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED until explicit human approval after product completeness closeout.
      </div>

      <div style={{ marginBottom: 16 }}>
        <button onClick={evaluate} disabled={evaluating}>
          {evaluating ? 'Evaluating...' : 'Run Evaluation'}
        </button>
        {status && <span style={{ color: 'green', marginLeft: 8 }}>{status}</span>}
        {error && <span style={{ color: 'red', marginLeft: 8 }}>{error}</span>}
      </div>

      {noReport && !record && (
        <p style={{ color: '#888' }}>No validation report yet. Run an evaluation to generate one.</p>
      )}

      {record && (
        <div style={{ padding: 14, background: '#f6f8ff', borderRadius: 6, border: '1px solid #d0daf0' }}>
          <h3 style={{ margin: '0 0 10px' }}>Validation Report</h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, marginBottom: 14 }}>
            <div>
              <strong style={{ color: OUTCOME_COLORS[record.outcome] || '#888', fontSize: 16 }}>
                {record.outcome.replace(/_/g, ' ')}
              </strong>
            </div>
            <div><strong>{record.weekly_review_count}</strong><br />weekly reviews</div>
            <div><strong>{record.calibration_record_count}</strong><br />calibration records</div>
            <div><strong>{record.pattern_review_count}</strong><br />pattern reviews</div>
            {record.evidence_window_days != null && (
              <div><strong>{record.evidence_window_days}</strong><br />evidence window (days)</div>
            )}
          </div>

          <div style={{ padding: 10, background: '#fff', borderRadius: 4, border: '1px solid #e0e0e0', marginBottom: 12 }}>
            <p style={{ margin: 0, fontSize: 14 }}>{record.message}</p>
          </div>

          <h4 style={{ margin: '0 0 8px' }}>Metrics</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 14 }}>
            <CheckItem label="Alignment improves" checked={record.metrics.action_alignment_score_improves} />
            <CheckItem label="Patterns reduce" checked={record.metrics.repeated_negative_patterns_reduce} />
            <CheckItem label="Correction rate improves" checked={record.metrics.primary_correction_completion_rate_improves} />
          </div>

          <h4 style={{ margin: '0 0 8px' }}>Usage Integrity</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 14 }}>
            <CheckItem label="Weekly notes honest" checked={record.usage_integrity.weekly_notes_completed_honestly} />
            <CheckItem label="Calibration records created" checked={record.usage_integrity.calibration_records_created} />
            <CheckItem label="Primary corrections set" checked={record.usage_integrity.primary_corrections_set} />
            <CheckItem label="Failure reviews honest" checked={record.usage_integrity.failure_reviews_honest} />
            <CheckItem label="Self-deception not softened" checked={record.usage_integrity.self_deception_risk_not_softened} />
            <CheckItem label="Sessions not skipped" checked={record.usage_integrity.sessions_not_skipped_too_often} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, fontSize: 13 }}>
            <div>Integrity valid: <strong>{record.usage_integrity_valid ? 'Yes' : 'No'}</strong></div>
            <div>Behavior improved: <strong>{record.behavior_improved ? 'Yes' : 'No'}</strong></div>
            <div>Evidence verified: <strong>{record.evidence_verified ? 'Yes' : 'No'}</strong></div>
          </div>

          {record.created_at && (
            <p style={{ fontSize: 12, color: '#888', marginTop: 10 }}>Evaluated: {record.created_at}</p>
          )}
        </div>
      )}
    </div>
  )
}

function CheckItem({ label, checked }: { label: string; checked: boolean }) {
  return (
    <div style={{ fontSize: 13, padding: 6, background: '#fff', borderRadius: 4, border: '1px solid #e0e0e0' }}>
      <span style={{ color: checked ? '#4caf50' : '#b00020', marginRight: 6 }}>
        {checked ? 'yes' : 'no'}
      </span>
      {label}
    </div>
  )
}
