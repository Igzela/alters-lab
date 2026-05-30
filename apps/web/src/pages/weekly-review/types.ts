import type { VerdictLabel } from '../../types'

export type Step = 1 | 2 | 3 | 4 | 5 | 6

export type AlterOption = { id: string; name: string }

export const NOTE_TEMPLATE = `# Weekly Review - ${new Date().toISOString().slice(0, 10)}

## Session Type
personal / project / learning / relationship

## Observable Facts
-
-
-
-
-

## Subjective State
1-3 sentences.

## Primary Problem
One sentence.

## Friction / Avoidance
One concrete friction or avoidance point.

## Desired Correction
One primary correction for next week.
`

export const VERDICTS: VerdictLabel[] = [
  'aligned_progress',
  'noisy_progress',
  'avoidance_disguised_as_work',
  'recovery_week',
  'unstable_but_useful',
  'blocked_by_environment',
]

export const VERDICT_DESCRIPTIONS: Record<VerdictLabel, string> = {
  aligned_progress: 'Actions matched your stated direction. You did what you intended.',
  noisy_progress: 'You made progress, but not in your intended direction. Some drift.',
  avoidance_disguised_as_work: 'Activity looked productive but avoided the real problem.',
  recovery_week: 'You bounced back from a stall or setback. Restorative week.',
  unstable_but_useful: 'Inconsistent, but some meaningful progress happened.',
  blocked_by_environment: 'External factors prevented progress despite intention.',
}
