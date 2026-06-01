import { Routes, Route, Navigate } from 'react-router-dom'
import SystemStatus from '../pages/SystemStatus'
import AlterDialogue from '../pages/AlterDialogue'
import RealityScore from '../pages/RealityScore'
import CalibrationHistory from '../pages/CalibrationHistory'
import RubricDelta from '../pages/RubricDelta'
import CheckpointPlan from '../pages/CheckpointPlan'
import ProviderSettings from '../pages/ProviderSettings'
import WeeklyReview from '../pages/WeeklyReview'
import GettingStarted from '../pages/GettingStarted'
import PatternReview from '../pages/PatternReview'
import BehaviorValidation from '../pages/BehaviorValidation'
import DataManagement from '../pages/DataManagement'
import Dashboard from '../pages/Dashboard'
import PredictorProfile from '../pages/PredictorProfile'
import OutcomeTargets from '../pages/OutcomeTargets'
import BranchForecast from '../pages/BranchForecast'
import ForecastCalibration from '../pages/ForecastCalibration'

export default function PageRouter() {
  return (
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
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
