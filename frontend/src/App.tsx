import { Route, Routes } from "react-router";

import { AppShell } from "@/components/layout/AppShell";
import { WorkspaceProvider } from "@/components/workspace/WorkspaceProvider";
import { CompetitorsPage } from "@/pages/CompetitorsPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { NewCompanyPage } from "@/pages/NewCompanyPage";
import { RunDetailPage } from "@/pages/RunDetailPage";
import { RunsPage } from "@/pages/RunsPage";
import { SettingsPage } from "@/pages/SettingsPage";

export function App() {
  return (
    <WorkspaceProvider>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="runs" element={<RunsPage />} />
          <Route path="runs/:runId" element={<RunDetailPage />} />
          <Route path="competitors" element={<CompetitorsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="companies/new" element={<NewCompanyPage />} />
        </Route>
      </Routes>
    </WorkspaceProvider>
  );
}
