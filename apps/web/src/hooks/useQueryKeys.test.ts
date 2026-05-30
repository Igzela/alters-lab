import { describe, it, expect } from 'vitest'
import { queryKeys } from './useQueryKeys'

describe('queryKeys', () => {
  it('returns array keys for static queries', () => {
    expect(queryKeys.weeklyNotes).toEqual(['weekly-notes'])
    expect(queryKeys.weeklyReviews).toEqual(['weekly-reviews'])
    expect(queryKeys.providerConfig).toEqual(['provider-config'])
    expect(queryKeys.providerStatus).toEqual(['provider-status'])
    expect(queryKeys.actionAlignmentScores).toEqual(['action-alignment-scores'])
    expect(queryKeys.calibrationHistory).toEqual(['calibration-history'])
    expect(queryKeys.productStatus).toEqual(['product-status'])
    expect(queryKeys.localAppStatus).toEqual(['local-app-status'])
    expect(queryKeys.runtimeStatus).toEqual(['runtime-status'])
    expect(queryKeys.alters).toEqual(['alters'])
    expect(queryKeys.dataManifest).toEqual(['data-manifest'])
  })

  it('returns parameterized keys for dynamic queries', () => {
    expect(queryKeys.trendAnalysis(8, 4)).toEqual(['trend-analysis', 8, 4])
    expect(queryKeys.dynamicWeights(8)).toEqual(['dynamic-weights', 8])
    expect(queryKeys.patternAdjustment(8, 4)).toEqual(['pattern-adjustment', 8, 4])
    expect(queryKeys.patternReviewDetail('abc123')).toEqual(['pattern-review', 'abc123'])
  })
})
