import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import LoadingSpinner from './LoadingSpinner'

const Dashboard = lazy(() => import('../pages/Dashboard'))
const SystemStatus = lazy(() => import('../pages/SystemStatus'))
const WeeklyReview = lazy(() => import('../pages/WeeklyReview'))
const AlterDialogue = lazy(() => import('../pages/AlterDialogue'))
const RealityScore = lazy(() => import('../pages/RealityScore'))
const CalibrationHistory = lazy(() => import('../pages/CalibrationHistory'))
const RubricDelta = lazy(() => import('../pages/RubricDelta'))
const CheckpointPlan = lazy(() => import('../pages/CheckpointPlan'))
const ProviderSettings = lazy(() => import('../pages/ProviderSettings'))
const GettingStarted = lazy(() => import('../pages/GettingStarted'))
const PatternReview = lazy(() => import('../pages/PatternReview'))
const BehaviorValidation = lazy(() => import('../pages/BehaviorValidation'))
const DataManagement = lazy(() => import('../pages/DataManagement'))
const PredictorProfile = lazy(() => import('../pages/PredictorProfile'))
const OutcomeTargets = lazy(() => import('../pages/OutcomeTargets'))
const BranchForecast = lazy(() => import('../pages/BranchForecast'))
const ForecastCalibration = lazy(() => import('../pages/ForecastCalibration'))
const PublicPriors = lazy(() => import('../pages/PublicPriors'))
const CalibrationConversation = lazy(() => import('../pages/CalibrationConversation'))
const BehaviorMetricsDetail = lazy(() => import('../pages/BehaviorMetricsDetail'))
const StrengthOverview = lazy(() => import('../pages/StrengthOverview'))
const P6Progress = lazy(() => import('../pages/P6Progress'))

export default function PageRouter() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-64"><LoadingSpinner /></div>}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/status" element={<SystemStatus />} />
        <Route path="/weekly" element={<WeeklyReview />} />
        <Route path="/dialogue" element={<AlterDialogue />} />
        <Route path="/reality" element={<RealityScore />} />
        <Route path="/history" element={<CalibrationHistory />} />
        <Route path="/rubric" element={<RubricDelta />} />
        <Route path="/checkpoint" element={<CheckpointPlan />} />
        <Route path="/provider" element={<ProviderSettings />} />
        <Route path="/getting-started" element={<GettingStarted />} />
        <Route path="/patterns" element={<PatternReview />} />
        <Route path="/validation" element={<BehaviorValidation />} />
        <Route path="/data" element={<DataManagement />} />
        <Route path="/predictor-profile" element={<PredictorProfile />} />
        <Route path="/outcome-targets" element={<OutcomeTargets />} />
        <Route path="/branch-forecast" element={<BranchForecast />} />
        <Route path="/forecast-calibration" element={<ForecastCalibration />} />
        <Route path="/public-priors" element={<PublicPriors />} />
        <Route path="/calibration-conversation" element={<CalibrationConversation />} />
        <Route path="/behavior-metrics" element={<BehaviorMetricsDetail />} />
        <Route path="/strength-overview" element={<StrengthOverview />} />
        <Route path="/p6-progress" element={<P6Progress />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
