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
  P6_BEHAVIOR_VALIDATED: 'text-green-400',
  P6_FAILED_TO_VALIDATE: 'text-orange-400',
  P6_USAGE_INVALID: 'text-red-500',
  P6_INSUFFICIENT_DATA: 'text-gray-400',
}

function CheckItem({ label, checked }: { label: string; checked: boolean }) {
  return (
    <div className="text-xs p-1.5 bg-gray-800/50 rounded border border-gray-700">
      <span className={checked ? 'text-green-400' : 'text-red-500'}>{checked ? 'yes' : 'no'}</span>
      {' '}{label}
    </div>
  )
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
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Behavior Validation</h2>
      <p className="text-gray-500 text-xs">
        Evaluates whether your behavior has improved based on weekly reviews, calibration records, and pattern reviews. This does NOT automatically validate P6.
      </p>

      <div className="p-3 bg-amber-950/30 border border-amber-800/50 rounded-lg mb-4">
        <strong className="text-sm">P6 validation status: Not started.</strong>
        <p className="text-xs text-gray-400 mt-1">P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED until explicit human approval after product completeness closeout.</p>
      </div>

      <div className="mb-4">
        <button
          className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50"
          onClick={evaluate}
          disabled={evaluating}
        >
          {evaluating ? 'Evaluating...' : 'Run Evaluation'}
        </button>
        {status && <span className="text-green-400 text-sm ml-2">{status}</span>}
        {error && <span className="text-red-500 text-sm ml-2">{error}</span>}
      </div>

      {noReport && !record && (
        <p className="text-gray-400 text-sm">No validation report yet. Run an evaluation to generate one.</p>
      )}

      {record && (
        <div className="p-3.5 bg-blue-950/30 rounded-lg border border-blue-800/30">
          <h3 className="text-sm font-medium mb-2">Validation Report</h3>

          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 mb-3">
            <div>
              <strong className={`text-base ${OUTCOME_COLORS[record.outcome] || 'text-gray-400'}`}>
                {record.outcome.replace(/_/g, ' ')}
              </strong>
            </div>
            <div className="text-sm"><strong>{record.weekly_review_count}</strong><br /><span className="text-gray-400 text-xs">weekly reviews</span></div>
            <div className="text-sm"><strong>{record.calibration_record_count}</strong><br /><span className="text-gray-400 text-xs">calibration records</span></div>
            <div className="text-sm"><strong>{record.pattern_review_count}</strong><br /><span className="text-gray-400 text-xs">pattern reviews</span></div>
            {record.evidence_window_days != null && (
              <div className="text-sm"><strong>{record.evidence_window_days}</strong><br /><span className="text-gray-400 text-xs">evidence window (days)</span></div>
            )}
          </div>

          <div className="p-2.5 bg-gray-800/50 rounded border border-gray-700 mb-3">
            <p className="text-sm">{record.message}</p>
          </div>

          <h4 className="text-sm font-medium mb-2">Metrics</h4>
          <div className="grid grid-cols-3 gap-2 mb-3">
            <CheckItem label="Alignment improves" checked={record.metrics.action_alignment_score_improves} />
            <CheckItem label="Patterns reduce" checked={record.metrics.repeated_negative_patterns_reduce} />
            <CheckItem label="Correction rate improves" checked={record.metrics.primary_correction_completion_rate_improves} />
          </div>

          <h4 className="text-sm font-medium mb-2">Usage Integrity</h4>
          <div className="grid grid-cols-2 gap-2 mb-3">
            <CheckItem label="Weekly notes honest" checked={record.usage_integrity.weekly_notes_completed_honestly} />
            <CheckItem label="Calibration records created" checked={record.usage_integrity.calibration_records_created} />
            <CheckItem label="Primary corrections set" checked={record.usage_integrity.primary_corrections_set} />
            <CheckItem label="Failure reviews honest" checked={record.usage_integrity.failure_reviews_honest} />
            <CheckItem label="Self-deception not softened" checked={record.usage_integrity.self_deception_risk_not_softened} />
            <CheckItem label="Sessions not skipped" checked={record.usage_integrity.sessions_not_skipped_too_often} />
          </div>

          <div className="grid grid-cols-3 gap-2.5 text-xs">
            <div>Integrity valid: <strong>{record.usage_integrity_valid ? 'Yes' : 'No'}</strong></div>
            <div>Behavior improved: <strong>{record.behavior_improved ? 'Yes' : 'No'}</strong></div>
            <div>Evidence verified: <strong>{record.evidence_verified ? 'Yes' : 'No'}</strong></div>
          </div>

          {record.created_at && (
            <p className="text-xs text-gray-500 mt-2">Evaluated: {record.created_at}</p>
          )}
        </div>
      )}
    </div>
  )
}
