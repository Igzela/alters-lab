import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { listActionAlignmentScores, listWeeklyNotes, listWeeklyReviews } from '../api'
import { Card } from '../components/Card'
import { ProgressBar } from '../components/ProgressBar'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

type Counts = {
  weeklyNotes: number
  weeklyReviews: number
  actionAlignment: number
}

export default function P6Progress() {
  const { t } = useTranslation()
  const [counts, setCounts] = useState<Counts | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([listWeeklyNotes(), listWeeklyReviews(), listActionAlignmentScores()])
      .then(([notes, reviews, scores]) => {
        setCounts({
          weeklyNotes: notes.count,
          weeklyReviews: reviews.count,
          actionAlignment: scores.count,
        })
      })
      .catch(e => setError(e instanceof Error ? e.message : t('p6Progress.unableToLoad')))
  }, [])

  const weeksComplete = counts ? Math.min(4, counts.weeklyReviews) : 0
  const scoresComplete = counts ? Math.min(4, counts.actionAlignment) : 0

  return (
    <Card>
      <h3 className="text-sm font-medium mb-2">{t('p6Progress.title')}</h3>
      {error && <ErrorDisplay message={`${t('p6Progress.progressUnavailable')} ${error}`} />}
      {!counts && !error && <LoadingSpinner label={t('p6Progress.loading')} />}
      {counts && (
        <>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 text-sm">
            <div><strong>{counts.weeklyNotes}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('p6Progress.weeklyNotesIngested')}</span></div>
            <div><strong>{counts.weeklyReviews}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('p6Progress.weeklyReviewsCompleted')}</span></div>
            <div><strong>{counts.actionAlignment}</strong><br /><span className="text-xs" style={{ color: '#7c7c6f' }}>{t('p6Progress.alignmentScoresRecorded')}</span></div>
          </div>

          <div className="mt-3">
            <ProgressBar value={weeksComplete} max={4} label={`${t('p6Progress.weeklyReviews')} ${weeksComplete}/4`} accent="lilac" />
            <ProgressBar value={scoresComplete} max={4} label={`${t('p6Progress.alignmentScores')} ${scoresComplete}/4`} accent="lilac" />
          </div>

          <div className="mt-2 text-xs" style={{ color: '#7c7c6f' }}>
            <strong>{t('p6Progress.nextStep')}</strong> {t('p6Progress.nextStepDesc')}
          </div>
        </>
      )}
      <p className="text-xs mt-2" style={{ color: '#7c7c6f' }}>{t('p6Progress.p6Validated')} | {t('p6Progress.p6Sealed')}</p>
    </Card>
  )
}
