import { vi } from 'vitest'
import type { UseQueryResult } from '@tanstack/react-query'

// Mock window.matchMedia (not in jsdom)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

function mockQuery<T>(data: T, overrides?: Partial<UseQueryResult<T>>): UseQueryResult<T> {
  return {
    data,
    isLoading: false,
    isPending: false,
    isSuccess: true,
    isError: false,
    error: null,
    refetch: vi.fn() as never,
    fetchStatus: 'idle',
    status: 'success',
    dataUpdatedAt: 0,
    errorUpdateCount: 0,
    errorUpdatedAt: 0,
    failureCount: 0,
    failureReason: null,
    fetchMeta: null,
    isFetched: true,
    isFetchedAfterMount: true,
    isFetching: false,
    isLoadingError: false,
    isPlaceholderData: false,
    isRefetchError: false,
    isRefetching: false,
    isStale: false,
    isEnabled: true,
    remove: vi.fn() as never,
    ...overrides,
  } as unknown as UseQueryResult<T>
}

function mockMutation(overrides?: Record<string, unknown>) {
  return {
    mutate: vi.fn(),
    mutateAsync: vi.fn(),
    isPending: false,
    isSuccess: false,
    isError: false,
    error: null,
    data: undefined,
    reset: vi.fn(),
    ...overrides,
  }
}

export const mockHooks = {
  useAlterReply: vi.fn(() => mockMutation()),
  useBehaviorValidationReport: vi.fn(() => mockQuery(null)),
  useEvaluateBehaviorValidation: vi.fn(() => mockMutation()),
  useSubmitRealityScore: vi.fn(() => mockMutation()),
  useDataManifest: vi.fn(() => mockQuery(null)),
  useExportData: vi.fn(() => mockMutation()),
  useDeleteData: vi.fn(() => mockMutation()),
  useProviderConfig: vi.fn(() => mockQuery({ mode: 'disabled', base_url: null, model: null, timeout_seconds: 30, secret_storage: 'keyring', key_name: 'api_key' })),
  useProviderStatus: vi.fn(() => mockQuery({ provider_mode: 'disabled', configured: false, base_url_configured: false, model_configured: false, api_key_configured: false, secret_storage: 'keyring', secrets_redacted: true, provider_output_persists_by_default: false, provider_output_can_write_active_yaml: false, provider_output_can_generate_reality_score: false })),
  useUpdateProviderConfig: vi.fn(() => mockMutation()),
  useStoreSecret: vi.fn(() => mockMutation()),
  useDeleteSecret: vi.fn(() => mockMutation()),
  useTestProvider: vi.fn(() => mockMutation()),
  useSuggestRubricDelta: vi.fn(() => mockMutation()),
  useGenerateCheckpointPlan: vi.fn(() => mockMutation()),
  useWeeklyReviews: vi.fn(() => mockQuery({ sessions: [], count: 0 })),
  useWeeklyNotes: vi.fn(() => mockQuery({ records: [], count: 0 })),
  useActionAlignmentScores: vi.fn(() => mockQuery({ scores: [], count: 0 })),
  usePatternReviews: vi.fn(() => mockQuery({ reviews: [], count: 0 })),
  usePatternReviewDetail: vi.fn(() => mockQuery(null)),
  useBuildPatternReview: vi.fn(() => mockMutation()),
  useCalibrationHistory: vi.fn(() => mockQuery({ records: [], count: 0 })),
  useTrendAnalysis: vi.fn(() => mockQuery(null)),
  useDynamicWeights: vi.fn(() => mockQuery(null)),
  usePatternAdjustment: vi.fn(() => mockQuery(null)),
  useProductStatus: vi.fn(() => mockQuery({ status: 'ok', storage_backend: 'yaml', no_secrets_exposed: true, safe_public_endpoints: ['/health'] })),
  useLocalAppStatus: vi.fn(() => mockQuery({ status: 'ok', frontend_available: true })),
  useRuntimeStatus: vi.fn(() => mockQuery({ mode: 'dev', config_path: '/tmp/config', product_data_dir: '/tmp/data' })),
}

vi.mock('../hooks/useApi', () => mockHooks)
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => children,
  LineChart: ({ children }: { children: React.ReactNode }) => children,
  Line: () => null,
  BarChart: ({ children }: { children: React.ReactNode }) => children,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
}))
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en', changeLanguage: vi.fn() },
  }),
  Trans: ({ children }: { children: React.ReactNode }) => children,
  initReactI18next: { type: '3rdParty', init: vi.fn() },
}))
vi.mock('../../animations', () => ({
  fadeIn: vi.fn(),
  expandIn: vi.fn(),
  collapseOut: vi.fn(),
  pulseSuccess: vi.fn(),
  shakeError: vi.fn(),
  staggerFadeIn: vi.fn(),
}))
vi.mock('../components/ThemeContext', () => ({
  useTheme: () => ({ theme: 'light' as const, toggleTheme: vi.fn() }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
}))
vi.mock('../hooks/usePredictionHooks', () => ({
  usePredictorProfiles: vi.fn(() => mockQuery({ profiles: [], count: 0 })),
  usePredictorProfile: vi.fn(() => mockQuery(null)),
  useCreatePredictorProfile: vi.fn(() => mockMutation()),
  useOutcomeTargets: vi.fn(() => mockQuery({ targets: [], count: 0 })),
  useCreateOutcomeTarget: vi.fn(() => mockMutation()),
  useEvaluateOutcomeTarget: vi.fn(() => mockMutation()),
  useBranchForecast: vi.fn(() => mockMutation()),
  useCalibrationDivergence: vi.fn(() => mockMutation()),
}))
vi.mock('../hooks/useForecastHooks', () => ({
  useForecastSnapshots: vi.fn(() => mockQuery({ snapshots: [], count: 0 })),
  useForecastSnapshot: vi.fn(() => mockQuery(null)),
  useCreateForecastSnapshot: vi.fn(() => mockMutation()),
  useExternalEvidence: vi.fn(() => mockQuery({ evidence: [], count: 0 })),
  useCreateExternalEvidence: vi.fn(() => mockMutation()),
  useForecastEvaluations: vi.fn(() => mockQuery({ evaluations: [], count: 0 })),
  useCreateForecastEvaluation: vi.fn(() => mockMutation()),
  useForecastScorecard: vi.fn(() => mockQuery(null)),
}))
vi.mock('../hooks/useMiscHooks', () => ({
  useFetchJson: vi.fn(() => mockQuery(null)),
  useSuggestRubricDelta: vi.fn(() => mockMutation()),
  useGenerateCheckpointPlan: vi.fn(() => mockMutation()),
}))
