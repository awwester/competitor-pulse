export type PageType = "pricing" | "changelog" | "blog" | "homepage" | "careers" | "docs" | "other";

export const PAGE_TYPES: PageType[] = [
  "pricing",
  "changelog",
  "blog",
  "homepage",
  "careers",
  "docs",
  "other",
];

export type RunStatus =
  | "queued"
  | "running"
  | "awaiting_review"
  | "published"
  | "applied"
  | "dismissed"
  | "no_changes"
  | "completed"
  | "failed";

export type RunKind = "check" | "company_discovery" | "page_discovery";

export type FindingCategory =
  | "pricing"
  | "product"
  | "positioning"
  | "hiring"
  | "content"
  | "other";

export type RunEventKind =
  | "phase"
  | "text"
  | "thinking"
  | "tool_call"
  | "tool_result"
  | "error"
  | "result";

export interface Meta {
  demoMode: boolean;
  agentModel: string;
  /** False when ANTHROPIC_API_KEY isn't set, so no agent can run. */
  agentConfigured: boolean;
  /** Local demo site offered on first run; null when not configured. */
  sampleCompanyUrl: string | null;
  nextCheckAt: string | null;
}

export interface Workspace {
  id: string;
  /** Null until discovery names the company. */
  name: string | null;
  website: string | null;
  companyProfile: string;
  slackConfigured: boolean;
  notifyEmails: string[];
}

export type WorkspaceInput = { website: string };

/** The Slack webhook is a secret: it can be set or cleared but is never sent back. */
export type WorkspaceUpdate = Partial<Omit<Workspace, "id" | "slackConfigured">> & {
  slackWebhookUrl?: string | null;
};

export interface TrackedPage {
  id: string;
  competitorId: string;
  url: string;
  pageType: PageType;
  isActive: boolean;
  rationale: string;
  createdAt: string;
}

export interface TrackedPageInput {
  url: string;
  pageType: PageType;
  isActive?: boolean;
}

export interface Competitor {
  id: string;
  name: string;
  website: string;
  notes: string;
  createdAt: string;
  pages: TrackedPage[];
}

export interface CompetitorInput {
  name: string;
  website: string;
  notes: string;
  pages?: TrackedPageInput[];
}

export interface Finding {
  id: string;
  runId: string;
  competitorId: string;
  competitorName: string;
  trackedPageId: string | null;
  sourceUrl: string | null;
  category: FindingCategory;
  significance: number;
  title: string;
  summary: string;
  evidence: string;
  recommendedAction: string;
  isDismissed: boolean;
  createdAt: string;
}

export interface CompetitorSuggestion {
  id: string;
  name: string;
  website: string;
  rationale: string;
  isSelected: boolean;
}

export interface SuggestionInput {
  name: string;
  website: string;
}

export interface RunSummary {
  id: string;
  kind: RunKind;
  competitorId: string | null;
  status: RunStatus;
  trigger: "manual" | "scheduled";
  createdAt: string;
  startedAt: string | null;
  finishedAt: string | null;
  headline: string | null;
  pagesChecked: number;
  pagesChanged: number;
  numTurns: number;
  inputTokens: number;
  outputTokens: number;
  cacheReadTokens: number;
  cacheWriteTokens: number;
  costUsd: number;
}

export interface RunDetail extends RunSummary {
  reportMarkdown: string | null;
  error: string | null;
  findings: Finding[];
  suggestions: CompetitorSuggestion[];
}

export interface RunEvent {
  id: string;
  seq: number;
  kind: RunEventKind;
  // Shape depends on kind; see backend app/agent/tracing.py
  payload: Record<string, unknown>;
  createdAt: string;
}

export interface Dashboard {
  competitorCount: number;
  pageCount: number;
  runCount: number;
  totalCostUsd: number;
  latestCheck: RunSummary | null;
  pendingReviews: RunSummary[];
  topFindings: Finding[];
}
