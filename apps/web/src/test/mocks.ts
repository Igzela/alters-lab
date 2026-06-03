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
  } as UseQueryResult<T>
}

export const mockHooks = {
  useWeeklyReviews: vi.fn(() => mockQuery({ sessions: [], count: 0 })),
  useWeeklyNotes: vi.fn(() => mockQuery({ records: [], count: 0 })),
  useActionAlignmentScores: vi.fn(() => mockQuery({ scores: [], count: 0 })),
  usePatternReviews: vi.fn(() => mockQuery({ reviews: [], count: 0 })),
  useCalibrationHistory: vi.fn(() => mockQuery({ records: [], count: 0 })),
  useTrendAnalysis: vi.fn(() => mockQuery(null)),
  useDynamicWeights: vi.fn(() => mockQuery(null)),
  usePatternAdjustment: vi.fn(() => mockQuery(null)),
  useProductStatus: vi.fn(() => mockQuery({ status: 'ok' })),
  useLocalAppStatus: vi.fn(() => mockQuery({ status: 'ok' })),
  useRuntimeStatus: vi.fn(() => mockQuery({ mode: 'dev' })),
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
