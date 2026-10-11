import axios, { isAxiosError } from "axios";

import type {
  Competitor,
  CompetitorInput,
  CompetitorSuggestion,
  Dashboard,
  Finding,
  Meta,
  RunDetail,
  RunEvent,
  RunSummary,
  SuggestionInput,
  TrackedPage,
  TrackedPageInput,
  Workspace,
  WorkspaceInput,
  WorkspaceUpdate,
} from "@/types/api";

const http = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/api/v1`,
});

const data = <T>(promise: Promise<{ data: T }>) => promise.then((r) => r.data);

/** The company every scoped call targets; set by `WorkspaceProvider` before anything renders. */
let workspaceId: string | null = null;

export function setWorkspaceId(id: string) {
  workspaceId = id;
}

const scoped = (path = "") => `/workspaces/${workspaceId}${path}`;

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

  workspaces: () => data(http.get<Workspace[]>("/workspaces")),
  createWorkspace: (body: WorkspaceInput) => data(http.post<Workspace>("/workspaces", body)),
  deleteWorkspace: (id: string) => http.delete(`/workspaces/${id}`),

  workspace: () => data(http.get<Workspace>(scoped())),
  updateWorkspace: (body: WorkspaceUpdate) => data(http.patch<Workspace>(scoped(), body)),
  dashboard: () => data(http.get<Dashboard>(scoped("/dashboard"))),

  competitors: () => data(http.get<Competitor[]>(scoped("/competitors"))),
  createCompetitor: (body: CompetitorInput) => data(http.post<Competitor>(scoped("/competitors"), body)),
  updateCompetitor: (id: string, body: Partial<CompetitorInput>) =>
    data(http.patch<Competitor>(scoped(`/competitors/${id}`), body)),
  deleteCompetitor: (id: string) => http.delete(scoped(`/competitors/${id}`)),
  discoverPages: (competitorId: string) =>
    data(http.post<RunSummary>(scoped(`/competitors/${competitorId}/discover`))),

  addPage: (competitorId: string, body: TrackedPageInput) =>
    data(http.post<TrackedPage>(scoped(`/competitors/${competitorId}/pages`), body)),
  updatePage: (id: string, body: Partial<TrackedPageInput>) =>
    data(http.patch<TrackedPage>(scoped(`/pages/${id}`), body)),
  deletePage: (id: string) => http.delete(scoped(`/pages/${id}`)),

  runs: () => data(http.get<RunSummary[]>(scoped("/runs"))),
  run: (id: string) => data(http.get<RunDetail>(scoped(`/runs/${id}`))),
  runEvents: (id: string) => data(http.get<RunEvent[]>(scoped(`/runs/${id}/events`))),
  createRun: () => data(http.post<RunSummary>(scoped("/runs"))),
  publishRun: (id: string) => data(http.post<RunDetail>(scoped(`/runs/${id}/publish`))),
  dismissRun: (id: string) => data(http.post<RunDetail>(scoped(`/runs/${id}/dismiss`))),
  updateFinding: (id: string, isDismissed: boolean) =>
    data(http.patch<Finding>(scoped(`/findings/${id}`), { isDismissed })),

  startDiscovery: (website: string) => data(http.post<RunSummary>(scoped("/discovery"), { website })),
  addSuggestion: (runId: string, body: SuggestionInput) =>
    data(http.post<CompetitorSuggestion>(scoped(`/runs/${runId}/suggestions`), body)),
  updateSuggestion: (id: string, isSelected: boolean) =>
    data(http.patch<CompetitorSuggestion>(scoped(`/suggestions/${id}`), { isSelected })),
  applyDiscovery: (runId: string) => data(http.post<RunDetail>(scoped(`/runs/${runId}/apply`))),
};
