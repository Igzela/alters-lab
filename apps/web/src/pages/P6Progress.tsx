import { useTranslation } from 'react-i18next'
import { useWeeklyNotes, useWeeklyReviews, useActionAlignmentScores } from '../hooks/useApi'
import { Card } from '../components/Card'
import { ProgressBar } from '../components/ProgressBar'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

export default function P6Progress() {
  const { t } = useTranslation()
  const notes = useWeeklyNotes()
  const reviews = useWeeklyReviews()
  const scores = useActionAlignmentScores()

  const error = notes.error || reviews.error || scores.error
  const isLoading = notes.isLoading || reviews.isLoading || scores.isLoading

  const weeklyNotesCount = notes.data?.count ?? 0
  const weeklyReviewsCount = reviews.data?.count ?? 0
  const alignmentScoresCount = scores.data?.count ?? 0

  const weeksComplete = Math.min(4, weeklyReviewsCount)
  const scoresComplete = Math.min(4, alignmentScoresCount)

  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('p6Progress.title')}</h3>
      {error && <ErrorDisplay message={`${t('p6Progress.progressUnavailable')} ${(error as Error).message}`} />}
      {isLoading && <LoadingSpinner label={t('p6Progress.loading')} />}
      {!isLoading && !error && (
        <>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 text-sm">
            <div><strong>{weeklyNotesCount}</strong><br /><span className="text-xs" style={{ color: '#a8a29e' }}>{t('p6Progress.weeklyNotesIngested')}</span></div>
            <div><strong>{weeklyReviewsCount}</strong><br /><span className="text-xs" style={{ color: '#a8a29e' }}>{t('p6Progress.weeklyReviewsCompleted')}</span></div>
            <div><strong>{alignmentScoresCount}</strong><br /><span className="text-xs" style={{ color: '#a8a29e' }}>{t('p6Progress.alignmentScoresRecorded')}</span></div>
          </div>

          <div className="mt-3">
            <ProgressBar value={weeksComplete} max={4} label={`${t('p6Progress.weeklyReviews')} ${weeksComplete}/4`} accent="amber" />
            <ProgressBar value={scoresComplete} max={4} label={`${t('p6Progress.alignmentScores')} ${scoresComplete}/4`} accent="amber" />
          </div>

          <div className="mt-2 text-xs" style={{ color: '#a8a29e' }}>
            <strong>{t('p6Progress.nextStep')}</strong> {t('p6Progress.nextStepDesc')}
          </div>
        </>
      )}
      <p className="text-xs mt-2" style={{ color: '#a8a29e' }}>{t('p6Progress.p6Validated')} | {t('p6Progress.p6Sealed')}</p>
    </Card>
  )
}
