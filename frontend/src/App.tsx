/**
 * Main App component with routing and authentication.
 */

import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { TourProvider } from "./components/onboarding/TourProvider";
import { ProtectedRoute } from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ItemsPage from "./pages/ItemsPage";
import LocationsPage from "./pages/LocationsPage";
import InventoryPage from "./pages/InventoryPage";
import BlueprintsPage from "./pages/BlueprintsPage";
import BlueprintDetailPage from "./pages/BlueprintDetailPage";
import BlueprintFormPage from "./pages/BlueprintFormPage";
import CraftsPage from "./pages/CraftsPage";
import CraftFormPage from "./pages/CraftFormPage";
import CraftDetailPage from "./pages/CraftDetailPage";
import GoalsPage from "./pages/GoalsPage";
import GoalFormPage from "./pages/GoalFormPage";
import GoalDetailPage from "./pages/GoalDetailPage";
import OptimizationSettingsPage from "./pages/OptimizationSettingsPage";
import AnalyticsConsentPage from "./pages/AnalyticsConsentPage";
import AnalyticsDashboardPage from "./pages/AnalyticsDashboardPage";
import IntegrationsPage from "./pages/IntegrationsPage";
import IntegrationFormPage from "./pages/IntegrationFormPage";
import IntegrationDetailPage from "./pages/IntegrationDetailPage";
import ImportExportPage from "./pages/ImportExportPage";
import ModerationDashboardPage from "./pages/ModerationDashboardPage";
import SubmissionDetailPage from "./pages/SubmissionDetailPage";
import SubmissionFormPage from "./pages/SubmissionFormPage";
import MySubmissionsPage from "./pages/MySubmissionsPage";
import PublicEntitiesPage from "./pages/PublicEntitiesPage";
import PublicEntityDetailPage from "./pages/PublicEntityDetailPage";
import TagManagerPage from "./pages/TagManagerPage";
import DuplicateFinderPage from "./pages/DuplicateFinderPage";

function App() {
  return (
    <AuthProvider>
      <TourProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/items"
            element={
              <ProtectedRoute>
                <ItemsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/locations"
            element={
              <ProtectedRoute>
                <LocationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inventory"
            element={
              <ProtectedRoute>
                <InventoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/blueprints"
            element={
              <ProtectedRoute>
                <BlueprintsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/blueprints/new"
            element={
              <ProtectedRoute>
                <BlueprintFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/blueprints/:id/edit"
            element={
              <ProtectedRoute>
                <BlueprintFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/blueprints/:id"
            element={
              <ProtectedRoute>
                <BlueprintDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/crafts"
            element={
              <ProtectedRoute>
                <CraftsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/crafts/new"
            element={
              <ProtectedRoute>
                <CraftFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/crafts/:id"
            element={
              <ProtectedRoute>
                <CraftDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/goals"
            element={
              <ProtectedRoute>
                <GoalsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/goals/new"
            element={
              <ProtectedRoute>
                <GoalFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/goals/:id/edit"
            element={
              <ProtectedRoute>
                <GoalFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/goals/:id"
            element={
              <ProtectedRoute>
                <GoalDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/optimization"
            element={
              <ProtectedRoute>
                <OptimizationSettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics/consent"
            element={
              <ProtectedRoute>
                <AnalyticsConsentPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <AnalyticsDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/integrations"
            element={
              <ProtectedRoute>
                <IntegrationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/integrations/new"
            element={
              <ProtectedRoute>
                <IntegrationFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/integrations/:id/edit"
            element={
              <ProtectedRoute>
                <IntegrationFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/integrations/:id"
            element={
              <ProtectedRoute>
                <IntegrationDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/import-export"
            element={
              <ProtectedRoute>
                <ImportExportPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/commons/my-submissions"
            element={
              <ProtectedRoute>
                <MySubmissionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/commons/submit"
            element={
              <ProtectedRoute>
                <SubmissionFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/commons/submissions/:id/edit"
            element={
              <ProtectedRoute>
                <SubmissionFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/commons/public"
            element={
              <ProtectedRoute>
                <PublicEntitiesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/commons/public/:entityType/:entityId"
            element={
              <ProtectedRoute>
                <PublicEntityDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/commons/submissions"
            element={
              <ProtectedRoute>
                <ModerationDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/commons/submissions/:id"
            element={
              <ProtectedRoute>
                <SubmissionDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/commons/tags"
            element={
              <ProtectedRoute>
                <TagManagerPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/commons/duplicates"
            element={
              <ProtectedRoute>
                <DuplicateFinderPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </TourProvider>
    </AuthProvider>
  );
}

export default App;
