import { useEffect, useState } from 'react'
import { listActionAlignmentScores, listWeeklyNotes, listWeeklyReviews } from '../api'

type Counts = {
  weeklyNotes: number
  weeklyReviews: number
  actionAlignment: number
}

export default function P6Progress() {
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
      .catch(e => setError(e instanceof Error ? e.message : 'Unable to load P6 progress'))
  }, [])

  const weeksComplete = counts ? Math.min(4, counts.weeklyReviews) : 0
  const scoresComplete = counts ? Math.min(4, counts.actionAlignment) : 0

  return (
    <section className="border border-gray-700 rounded-lg p-3.5 mb-4 bg-gray-800/20">
      <h3 className="text-sm font-medium mb-2">Your Progress</h3>
      {error && <p className="text-red-500 text-sm">Progress unavailable: {error}</p>}
      {!counts && !error && <p className="text-gray-400 text-sm">Loading progress...</p>}
      {counts && (
        <>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-2.5 text-sm">
            <div><strong>{counts.weeklyNotes}</strong><br /><span className="text-gray-400 text-xs">weekly notes ingested</span></div>
            <div><strong>{counts.weeklyReviews}</strong><br /><span className="text-gray-400 text-xs">weekly reviews completed</span></div>
            <div><strong>{counts.actionAlignment}</strong><br /><span className="text-gray-400 text-xs">alignment scores recorded</span></div>
          </div>

          <div className="mt-3 p-3 bg-gray-800/50 rounded border border-gray-700">
            <h4 className="text-sm font-medium mb-1.5">Validation Status</h4>
            <p className="text-sm mb-1">
              <strong>Not started.</strong> P6 validation requires 4 weekly reviews and 4 calibration records across 21+ days.
            </p>
            <p className="text-xs text-gray-400">
              Weekly reviews: {weeksComplete}/4 | Alignment scores: {scoresComplete}/4 | 4-week window: not yet met
            </p>
          </div>

          <div className="mt-2 text-xs text-gray-400">
            <strong>Next step:</strong> Continue weekly reviews as pilot evidence; P6 validation start remains blocked until product completeness closeout.
          </div>
        </>
      )}
      <p className="text-xs text-gray-500 mt-2">P6 behavior validated: false | P6 sealed: false</p>
    </section>
  )
}
