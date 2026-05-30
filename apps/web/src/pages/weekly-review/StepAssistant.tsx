import { useTranslation } from 'react-i18next'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Input, Field, Select, TextArea } from '../../components/Input'
import { Badge } from '../../components/Badge'
import { Banner } from '../../components/Banner'
import type { WeeklyReviewSession } from '../../types'

type Props = {
  session: WeeklyReviewSession
  reviewNote: string
  setReviewNote: (v: string) => void
  dialogueSummary: string
  setDialogueSummary: (v: string) => void
  primaryNextCorrection: string
  setPrimaryNextCorrection: (v: string) => void
  supportingAction1: string
  setSupportingAction1: (v: string) => void
  supportingAction2: string
  setSupportingAction2: (v: string) => void
  assistantHelp: string
  setAssistantHelp: (v: string) => void
  assistantSuggestion: string
  assistantStatus: { provider_mode: string; configured: boolean } | null
  assistantLiveConfirmation: string
  setAssistantLiveConfirmation: (v: string) => void
  assistantLoading: boolean
  assistantError: string
  loading: string
  onCheckProvider: () => void
  onGenerateSuggestion: (live: boolean) => void
  onCompleteReview: () => void
}

export default function StepAssistant({
  session, reviewNote, setReviewNote, dialogueSummary, setDialogueSummary,
  primaryNextCorrection, setPrimaryNextCorrection, supportingAction1, setSupportingAction1,
  supportingAction2, setSupportingAction2, assistantHelp, setAssistantHelp,
  assistantSuggestion, assistantStatus, assistantLiveConfirmation, setAssistantLiveConfirmation,
  assistantLoading, assistantError, loading, onCheckProvider, onGenerateSuggestion, onCompleteReview,
}: Props) {
  const { t } = useTranslation()
  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('weeklyReview.step4Title')}</h3>
      <Field label={t('weeklyReview.reviewNote')}>
        <TextArea value={reviewNote} onChange={e => setReviewNote(e.target.value)} rows={4} />
      </Field>
      <Field label={t('weeklyReview.dialogueSummary')}>
        <TextArea value={dialogueSummary} onChange={e => setDialogueSummary(e.target.value)} rows={4} />
      </Field>
      <Field label={t('weeklyReview.primaryNextCorrection')}>
        <Input value={primaryNextCorrection} onChange={e => setPrimaryNextCorrection(e.target.value)} />
      </Field>
      <Field label={t('weeklyReview.supportingAction1')}>
        <Input value={supportingAction1} onChange={e => setSupportingAction1(e.target.value)} />
      </Field>
      <Field label={t('weeklyReview.supportingAction2')}>
        <Input value={supportingAction2} onChange={e => setSupportingAction2(e.target.value)} />
      </Field>

      <Card variant="raised">
        <h4 className="text-sm font-medium mb-1.5">{t('weeklyReview.assistantSuggestion')}</h4>
        <p className="text-xs mb-2" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.providerAdvisory')}</p>
        <Field label={t('weeklyReview.requestedHelp')}>
          <Select value={assistantHelp} onChange={e => setAssistantHelp(e.target.value)}>
            <option value="general_review_suggestion">{t('weeklyReview.generalSuggestion')}</option>
            <option value="summarize_facts">{t('weeklyReview.summarizeFacts')}</option>
            <option value="identify_friction">{t('weeklyReview.identifyFriction')}</option>
            <option value="draft_primary_correction">{t('weeklyReview.draftCorrection')}</option>
            <option value="suggest_supporting_actions">{t('weeklyReview.suggestActions')}</option>
            <option value="challenge_avoidance">{t('weeklyReview.challengeAvoidance')}</option>
          </Select>
        </Field>
        <div className="flex gap-2 flex-wrap mb-2.5">
          <Button variant="secondary" onClick={onCheckProvider} disabled={assistantLoading}>
            {t('weeklyReview.checkProvider')}
          </Button>
          <Button variant="secondary" onClick={() => onGenerateSuggestion(false)} disabled={!!loading || assistantLoading}>
            {loading === 'generating suggestion' ? t('weeklyReview.generating') : t('weeklyReview.generateDryRun')}
          </Button>
        </div>
        {assistantStatus && (
          <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{t('weeklyReview.providerMode')} {assistantStatus.provider_mode} | {t('provider.configured')} <Badge variant={assistantStatus.configured ? 'success' : 'muted'}>{assistantStatus.configured ? 'yes' : 'no'}</Badge></p>
        )}
        {assistantStatus?.configured && assistantStatus.provider_mode === 'openai-compatible-http' && (
          <div className="mt-2">
            <Field label={t('weeklyReview.liveConfirmation')}>
              <Input value={assistantLiveConfirmation} onChange={e => setAssistantLiveConfirmation(e.target.value)} placeholder="run-live-weekly-review-assistant" />
            </Field>
            <Button variant="primary" onClick={() => onGenerateSuggestion(true)} disabled={!!loading || assistantLoading || assistantLiveConfirmation !== 'run-live-weekly-review-assistant'}>
              {t('weeklyReview.generateLive')}
            </Button>
          </div>
        )}
        {assistantError && <Banner variant="error" className="mt-2">{assistantError}</Banner>}
        {assistantSuggestion && (
          <div className="mt-3 p-3 rounded-xl" style={{ backgroundColor: 'var(--color-accent-light)', color: 'var(--color-text)' }}>
            <p className="text-xs font-semibold mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>{t('weeklyReview.unverifiedSuggestion')}</p>
            <pre className="whitespace-pre-wrap text-sm m-0" style={{ color: 'var(--color-text)' }}>{assistantSuggestion}</pre>
            <div className="flex gap-2 mt-2 flex-wrap">
              <Button variant="secondary" onClick={() => setReviewNote(assistantSuggestion)}>
                {t('weeklyReview.copyToReviewNote')}
              </Button>
              <Button variant="secondary" onClick={() => setDialogueSummary(assistantSuggestion)}>
                {t('weeklyReview.copyToDialogue')}
              </Button>
              <Button variant="secondary" onClick={() => setPrimaryNextCorrection(assistantSuggestion)}>
                {t('weeklyReview.copyToCorrection')}
              </Button>
            </div>
          </div>
        )}
      </Card>

      <div className="mt-3">
        <Button variant="primary" onClick={onCompleteReview} disabled={!!loading || !reviewNote.trim() || !primaryNextCorrection.trim()}>
          {loading === 'completing review' ? t('weeklyReview.completing') : t('weeklyReview.completeReview')}
        </Button>
      </div>
      {session.status === 'completed' && (
        <div className="mt-2 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          <p>{t('weeklyReview.statusCompleted')}</p>
          <p>{t('weeklyReview.nextCorrection')} {session.next_week_primary_correction}</p>
          <p>{t('weeklyReview.supportingActions')} {session.supporting_actions.join(', ') || t('weeklyReview.none')}</p>
        </div>
      )}
    </Card>
  )
}
