import axios, { isAxiosError } from "axios";

import type {
  Competitor,
  CompetitorInput,
  Dashboard,
  Finding,
  Meta,
  RunDetail,
  RunEvent,
  RunSummary,
  TrackedPage,
  TrackedPageInput,
  Workspace,
  WorkspaceUpdate,
} from "@/types/api";

const http = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/api/v1`,
});

const data = <T>(promise: Promise<{ data: T }>) => promise.then((r) => r.data);

export function errorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  }
  return error instanceof Error ? error.message : "Something went wrong";
}

export const api = {
  meta: () => data(http.get<Meta>("/meta")),
  dashboard: () => data(http.get<Dashboard>("/dashboard")),

  workspace: () => data(http.get<Workspace>("/workspace")),
  updateWorkspace: (body: WorkspaceUpdate) => data(http.patch<Workspace>("/workspace", body)),

  competitors: () => data(http.get<Competitor[]>("/competitors")),
  createCompetitor: (body: CompetitorInput) => data(http.post<Competitor>("/competitors", body)),
  updateCompetitor: (id: string, body: Partial<CompetitorInput>) =>
    data(http.patch<Competitor>(`/competitors/${id}`, body)),
  deleteCompetitor: (id: string) => http.delete(`/competitors/${id}`),

  addPage: (competitorId: string, body: TrackedPageInput) =>
    data(http.post<TrackedPage>(`/competitors/${competitorId}/pages`, body)),
  updatePage: (id: string, body: Partial<TrackedPageInput>) =>
    data(http.patch<TrackedPage>(`/pages/${id}`, body)),
  deletePage: (id: string) => http.delete(`/pages/${id}`),

  runs: () => data(http.get<RunSummary[]>("/runs")),
  run: (id: string) => data(http.get<RunDetail>(`/runs/${id}`)),
  runEvents: (id: string) => data(http.get<RunEvent[]>(`/runs/${id}/events`)),
  createRun: () => data(http.post<RunSummary>("/runs")),
  publishRun: (id: string) => data(http.post<RunDetail>(`/runs/${id}/publish`)),
  dismissRun: (id: string) => data(http.post<RunDetail>(`/runs/${id}/dismiss`)),
  updateFinding: (id: string, isDismissed: boolean) =>
    data(http.patch<Finding>(`/findings/${id}`, { isDismissed })),
};
