import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  useStartCalibrationConversation,
  useSendCalibrationMessage,
  useCalibrationConversation,
  useCalibrationDrafts,
  useConfirmCalibrationDraft,
  useRejectCalibrationDraft,
} from '../hooks/useApi'
import { fadeIn } from '../animations'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'
import { Banner } from '../components/Banner'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

// Strip <extraction>...</extraction> blocks from display text
function stripExtractionBlocks(text: string): string {
  return text.replace(/<extraction>[\s\S]*?<\/extraction>/g, '').trim()
}

const CONFIDENCE_VARIANTS: Record<string, 'success' | 'warning' | 'error'> = {
  high: 'success',
  medium: 'warning',
  low: 'error',
}

const RUBRIC_KEYS = ['execution_discipline', 'exploration_freedom', 'life_state_match', 'energy_level'] as const

const RUBRIC_KEY_MAP: Record<string, string> = {
  execution_discipline: 'calConversation.fields.executionDiscipline',
  exploration_freedom: 'calConversation.fields.explorationFreedom',
  life_state_match: 'calConversation.fields.lifeStateMatch',
  energy_level: 'calConversation.fields.energyLevel',
}

const BEHAVIOR_METRIC_KEY_MAP: Record<string, string> = {
  career_education_deep_work_minutes: 'behaviorMetrics.metrics.career_education_deep_work_minutes',
  planned_commitment_follow_through_rate: 'behaviorMetrics.metrics.planned_commitment_follow_through_rate',
  expense_logged_days: 'behaviorMetrics.metrics.expense_logged_days',
  regular_sleep_nights: 'behaviorMetrics.metrics.regular_sleep_nights',
  moderate_vigorous_activity_minutes: 'behaviorMetrics.metrics.moderate_vigorous_activity_minutes',
  avoidable_health_risk_events: 'behaviorMetrics.metrics.avoidable_health_risk_events',
  meaningful_social_contact_count: 'behaviorMetrics.metrics.meaningful_social_contact_count',
  abandoned_committed_blocks: 'behaviorMetrics.metrics.abandoned_committed_blocks',
  key_milestone_progress_pct: 'behaviorMetrics.metrics.key_milestone_progress_pct',
}

interface DraftCardProps {
  draft: Record<string, unknown>
  onConfirm: (id: string) => void
  onReject: (id: string) => void
  confirming: boolean
  rejecting: boolean
}

function DraftCard({ draft, onConfirm, onReject, confirming, rejecting }: DraftCardProps) {
  const { t } = useTranslation()
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (ref.current) fadeIn(ref.current)
  }, [])

  const behaviorMetrics = draft.behavior_metrics as Record<string, unknown> | null
  const rubricScores = draft.rubric_scores as Record<string, number> | null
  const externalEvidence = (draft.external_evidence as Array<Record<string, unknown>>) || []
  const outcomeTargets = (draft.outcome_targets as Array<Record<string, unknown>>) || []
  const predictorProfile = draft.predictor_profile as Record<string, unknown> | null
  const bigFive = predictorProfile?.big_five as Record<string, number> | null
  const currentContext = predictorProfile?.current_context as Record<string, unknown> | null
  const healthConstraints = ((predictorProfile?.health_constraints as string[]) || [])
  const confidence = (draft.extraction_confidence as string) || 'low'
  const reasoning = (draft.llm_reasoning as string) || ''
  const draftId = draft.draft_id as string

  return (
    <div ref={ref}>
      <Card accent="amber">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium">{t('calConversation.draft.title')}</h4>
          <span
            className="text-xs px-2 py-0.5 rounded-full font-medium"
            style={{
              backgroundColor: `var(--color-${CONFIDENCE_VARIANTS[confidence]}-light)`,
              color: `var(--color-${CONFIDENCE_VARIANTS[confidence]})`,
            }}
          >
            {t(`calConversation.draft.confidence.${confidence}`)}
          </span>
        </div>

        {behaviorMetrics && (
          <div className="mb-3">
            <h5 className="text-xs font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
              {t('calConversation.draft.behaviorMetrics')}
            </h5>
            <div className="grid grid-cols-2 gap-1.5 text-xs">
              {Object.entries(behaviorMetrics).map(([key, val]) => {
                if (val == null || val === '') return null
                return (
                  <div key={key} className="flex justify-between px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-surface-raised)' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>{t(BEHAVIOR_METRIC_KEY_MAP[key] || key)}</span>
                    <span className="font-mono" style={{ color: 'var(--color-text)' }}>{String(val)}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {rubricScores && (
          <div className="mb-3">
            <h5 className="text-xs font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
              {t('calConversation.draft.rubricScores')}
            </h5>
            <div className="grid grid-cols-2 gap-1.5 text-xs">
              {RUBRIC_KEYS.map(key => {
                const val = rubricScores[key]
                if (val == null) return null
                return (
                  <div key={key} className="flex justify-between px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-surface-raised)' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>{t(RUBRIC_KEY_MAP[key] || key)}</span>
                    <span className="font-mono" style={{ color: 'var(--color-text)' }}>{t('calConversation.rubricScoreValue', { value: val })}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {externalEvidence.length > 0 && (
          <div className="mb-3">
            <h5 className="text-xs font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
              {t('calConversation.draft.externalEvidence')}
            </h5>
            <ul className="space-y-1 text-xs list-disc pl-4">
              {externalEvidence.map((ev, i) => (
                <li key={i}>
                  <span className="font-medium">{t(`calConversation.evidenceDomains.${ev.domain as string}`, { defaultValue: (ev.domain as string).replace(/_/g, ' ') })}</span>
                  {': '}
                  <span style={{ color: 'var(--color-text-secondary)' }}>{ev.description as string}</span>
                  {' '}
                  <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                    ({t(`calConversation.evidenceStrength.${ev.objective_strength as string}`, { defaultValue: ev.objective_strength as string })})
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {outcomeTargets.length > 0 && (
          <div className="mb-3">
            <h5 className="text-xs font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
              {t('calConversation.draft.outcomeTargets')}
            </h5>
            <div className="space-y-2">
              {outcomeTargets.map((target, i) => {
                const name = target.outcome_name as string | undefined
                const domain = target.domain as string | undefined
                const horizon = target.horizon_months as number | undefined
                const objDef = target.objective_definition as string | undefined
                const threshold = target.success_threshold as string | undefined
                const method = target.measurement_method as string | undefined
                return (
                  <div key={i} className="rounded p-2 text-xs" style={{ backgroundColor: 'var(--color-surface-raised)' }}>
                    {name && <p className="font-medium mb-1">{name}</p>}
                    <div className="grid grid-cols-2 gap-1.5">
                      {domain && (
                        <div className="flex justify-between px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-surface)' }}>
                          <span style={{ color: 'var(--color-text-muted)' }}>{t('outcomeTargets.domain')}</span>
                          <span className="font-mono" style={{ color: 'var(--color-text)' }}>{domain}</span>
                        </div>
                      )}
                      {horizon != null && (
                        <div className="flex justify-between px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-surface)' }}>
                          <span style={{ color: 'var(--color-text-muted)' }}>{t('calConversation.fields.horizonMonths')}</span>
                          <span className="font-mono" style={{ color: 'var(--color-text)' }}>{horizon}</span>
                        </div>
                      )}
                    </div>
                    {objDef && <p className="mt-1" style={{ color: 'var(--color-text-secondary)' }}>{objDef}</p>}
                    {threshold && (
                      <p className="mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
                        {t('outcomeTargets.threshold')}: {threshold}
                      </p>
                    )}
                    {method && (
                      <p className="mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
                        {t('outcomeTargets.measurement')}: {method}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {predictorProfile && (
          <div className="mb-3">
            <h5 className="text-xs font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
              {t('calConversation.draft.predictorProfile')}
            </h5>

            {bigFive && (
              <div className="mb-2">
                <p className="text-xs mb-1" style={{ color: 'var(--color-text-muted)' }}>{t('calConversation.draft.traits')}</p>
                <div className="grid grid-cols-2 gap-1.5 text-xs">
                  {(['conscientiousness', 'neuroticism', 'extraversion', 'agreeableness', 'openness'] as const).map(trait => {
                    const val = bigFive[trait]
                    if (val == null) return null
                    return (
                      <div key={trait} className="flex justify-between px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-surface-raised)' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>{t(`calConversation.fields.${trait}`)}</span>
                        <span className="font-mono" style={{ color: 'var(--color-text)' }}>{String(val)}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {currentContext && (
              <div className="mb-2">
                <p className="text-xs mb-1" style={{ color: 'var(--color-text-muted)' }}>{t('calConversation.draft.context')}</p>
                <div className="grid grid-cols-2 gap-1.5 text-xs">
                  {(['education_status', 'employment_status', 'financial_stability', 'relationship_status'] as const).map(field => {
                    const val = currentContext[field] as string | undefined
                    if (!val) return null
                    const labelKey = field.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase()).replace(/Status$/, 'Status')
                    return (
                      <div key={field} className="flex justify-between px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-surface-raised)' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>{t(`calConversation.fields.${labelKey}`)}</span>
                        <span className="font-mono" style={{ color: 'var(--color-text)' }}>{val}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {healthConstraints.length > 0 && (
              <div>
                <p className="text-xs mb-1" style={{ color: 'var(--color-text-muted)' }}>{t('calConversation.fields.healthConstraints')}</p>
                <ul className="space-y-0.5 text-xs list-disc pl-4">
                  {healthConstraints.map((item, i) => (
                    <li key={i} style={{ color: 'var(--color-text-secondary)' }}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {reasoning && (
          <p className="text-xs mb-3 italic" style={{ color: 'var(--color-text-muted)' }}>
            {reasoning}
          </p>
        )}

        <div className="flex gap-2">
          <Button variant="primary" onClick={() => onConfirm(draftId)} disabled={confirming}>
            {confirming ? t('common.sending') : t('calConversation.draft.confirm')}
          </Button>
          <Button variant="danger" onClick={() => onReject(draftId)} disabled={rejecting}>
            {rejecting ? t('common.sending') : t('calConversation.draft.reject')}
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default function CalibrationConversation() {
  const { t } = useTranslation()
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const lastMessageRef = useRef<HTMLDivElement>(null)

  const startMutation = useStartCalibrationConversation()
  const sendMutation = useSendCalibrationMessage()
  const conversationQuery = useCalibrationConversation(conversationId)
  const draftsQuery = useCalibrationDrafts()
  const confirmMutation = useConfirmCalibrationDraft()
  const rejectMutation = useRejectCalibrationDraft()

  const conversation = conversationQuery.data as Record<string, unknown> | undefined
  const messages = (conversation?.messages as Array<Record<string, unknown>>) || []
  const pendingDrafts = ((draftsQuery.data as Record<string, unknown>)?.drafts as Array<Record<string, unknown>> || [])
    .filter(d => d.status === 'pending')

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  // Animate last message
  useEffect(() => {
    if (lastMessageRef.current && messages.length > 0) {
      fadeIn(lastMessageRef.current)
    }
  }, [messages.length])

  const startConversation = () => {
    startMutation.mutate(
      {},
      {
        onSuccess: (res) => {
          const data = res as Record<string, unknown>
          setConversationId(data.conversation_id as string)
        },
      }
    )
  }

  const send = () => {
    if (!message.trim() || !conversationId) return
    setMessage('')
    sendMutation.mutate({ conversationId, message: message.trim() })
  }

  const confirmDraft = (draftId: string) => {
    confirmMutation.mutate({ draftId })
  }

  const rejectDraft = (draftId: string) => {
    rejectMutation.mutate({ draftId })
  }

  // No active conversation: show start screen
  if (!conversationId) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-bold tracking-tight" style={{ color: 'var(--color-text)' }}>{t('calConversation.title')}</h2>
        <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('calConversation.description')}</p>
        <Button variant="primary" onClick={startConversation} disabled={startMutation.isPending}>
          {startMutation.isPending ? t('common.sending') : t('calConversation.start')}
        </Button>
        {startMutation.error && <ErrorDisplay message={(startMutation.error as Error).message} />}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ color: 'var(--color-text)' }}>{t('calConversation.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('calConversation.description')}</p>

      {conversationQuery.isLoading && <LoadingSpinner label={t('common.loading')} />}
      {conversationQuery.error && <ErrorDisplay message={(conversationQuery.error as Error).message} />}

      {/* Message history */}
      {messages.length > 0 && (
        <Card>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {messages.map((msg, i) => {
              const role = msg.role as string
              const content = stripExtractionBlocks(msg.content as string)
              if (!content) return null
              const isLast = i === messages.length - 1
              return (
                <div
                  key={i}
                  ref={isLast ? lastMessageRef : undefined}
                  className="text-sm"
                >
                  <strong
                    className="text-xs font-medium"
                    style={{
                      color: role === 'user' ? 'var(--color-accent)' : 'var(--color-text-secondary)',
                    }}
                  >
                    {role === 'user' ? t('calConversation.you') : t('calConversation.assistant')}
                  </strong>
                  <p className="whitespace-pre-wrap mt-0.5" style={{ color: 'var(--color-text)' }}>{content}</p>
                </div>
              )
            })}
            <div ref={messagesEndRef} />
          </div>
        </Card>
      )}

      {/* Pending drafts */}
      {pendingDrafts.length > 0 && (
        <div>
          <h3 className="text-sm font-medium mb-2">{t('calConversation.pendingDrafts')}</h3>
          {pendingDrafts.map(draft => (
            <DraftCard
              key={draft.draft_id as string}
              draft={draft}
              onConfirm={confirmDraft}
              onReject={rejectDraft}
              confirming={confirmMutation.isPending}
              rejecting={rejectMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2">
        <Input
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder={t('calConversation.placeholder')}
          aria-label={t('calConversation.placeholder')}
          className="flex-1"
        />
        <Button variant="primary" onClick={send} disabled={sendMutation.isPending || !message.trim()}>
          {sendMutation.isPending ? t('common.sending') : t('calConversation.send')}
        </Button>
      </div>

      {sendMutation.error && <Banner variant="error">{(sendMutation.error as Error).message}</Banner>}
      {confirmMutation.error && <Banner variant="error">{(confirmMutation.error as Error).message}</Banner>}
      {rejectMutation.error && <Banner variant="error">{(rejectMutation.error as Error).message}</Banner>}
    </div>
  )
}
