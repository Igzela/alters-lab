import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { listActionAlignmentScores, listWeeklyNotes, listWeeklyReviews } from '../api'
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
    <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
      <h3 className="text-sm font-medium mb-2">{t('p6Progress.title')}</h3>
      {error && <ErrorDisplay message={`${t('p6Progress.progressUnavailable')} ${error}`} />}
      {!counts && !error && <LoadingSpinner label={t('p6Progress.loading')} />}
      {counts && (
        <>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 text-sm">
            <div><strong>{counts.weeklyNotes}</strong><br /><span className="text-gray-400 text-xs">{t('p6Progress.weeklyNotesIngested')}</span></div>
            <div><strong>{counts.weeklyReviews}</strong><br /><span className="text-gray-400 text-xs">{t('p6Progress.weeklyReviewsCompleted')}</span></div>
            <div><strong>{counts.actionAlignment}</strong><br /><span className="text-gray-400 text-xs">{t('p6Progress.alignmentScoresRecorded')}</span></div>
          </div>

          <div className="mt-3 p-3 bg-gray-800/50 rounded border border-gray-700">
            <h4 className="text-sm font-medium mb-1.5">{t('p6Progress.validationStatus')}</h4>
            <p className="text-sm mb-1">
              <strong>{t('p6Progress.notStarted')}</strong> {t('p6Progress.validationRequires')}
            </p>
            <p className="text-xs text-gray-400">
              {t('p6Progress.weeklyReviews')} {weeksComplete}/4 | {t('p6Progress.alignmentScores')} {scoresComplete}/4 | {t('p6Progress.fourWeekWindow')}
            </p>
          </div>

          <div className="mt-2 text-xs text-gray-400">
            <strong>{t('p6Progress.nextStep')}</strong> {t('p6Progress.nextStepDesc')}
          </div>
        </>
      )}
      <p className="text-xs text-gray-500 mt-2">{t('p6Progress.p6Validated')} | {t('p6Progress.p6Sealed')}</p>
    </section>
  )
}
