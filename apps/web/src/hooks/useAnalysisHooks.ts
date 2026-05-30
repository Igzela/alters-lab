import { useQuery } from '@tanstack/react-query'
import { analyzeTrend, computeDynamicWeights, adjustForecast } from '../api'
import { queryKeys } from './useQueryKeys'

export function useTrendAnalysis(lookbackWeeks = 8, forecastWeeks = 4) {
  return useQuery({
    queryKey: queryKeys.trendAnalysis(lookbackWeeks, forecastWeeks),
    queryFn: () => analyzeTrend({ lookback_weeks: lookbackWeeks, forecast_weeks: forecastWeeks }),
  })
}

export function useDynamicWeights(lookbackWeeks = 8) {
  return useQuery({
    queryKey: queryKeys.dynamicWeights(lookbackWeeks),
    queryFn: () => computeDynamicWeights({ lookback_weeks: lookbackWeeks }),
  })
}

export function usePatternAdjustment(lookbackWeeks = 8, forecastWeeks = 4) {
  return useQuery({
    queryKey: queryKeys.patternAdjustment(lookbackWeeks, forecastWeeks),
    queryFn: () => adjustForecast({ lookback_weeks: lookbackWeeks, forecast_weeks: forecastWeeks }),
  })
}
