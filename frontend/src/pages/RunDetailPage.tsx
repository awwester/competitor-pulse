import type { ComponentType } from "react";
import { Link, useParams } from "react-router";

import { CompanyDiscoveryView } from "@/components/discovery/CompanyDiscoveryView";
import { PageDiscoveryView } from "@/components/discovery/PageDiscoveryView";
import { CheckRunView } from "@/components/runs/CheckRunView";
import { RunStats } from "@/components/runs/RunStats";
import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { RunTrace } from "@/components/runs/RunTrace";
import { isActive, RUN_KIND_LABELS, useRun, useRunEvents } from "@/hooks/useRuns";
import { formatDate } from "@/lib/format";
import type { RunDetail, RunKind } from "@/types/api";

const VIEWS: Record<RunKind, ComponentType<{ run: RunDetail; live: boolean }>> = {
  check: CheckRunView,
  company_discovery: CompanyDiscoveryView,
  page_discovery: PageDiscoveryView,
};

const IN_PROGRESS: Record<RunKind, string> = {
  check: "Checking competitors…",
  company_discovery: "Reading your site and looking for competitors…",
  page_discovery: "Finding pages worth watching…",
};

export function RunDetailPage() {
  const { runId = "" } = useParams();
  const { data: run } = useRun(runId);
  const live = isActive(run?.status);
  const { data: events = [] } = useRunEvents(runId, run?.status);

  if (!run) return null;
  const View = VIEWS[run.kind];

  return (
    <div className="space-y-10">
      <header className="space-y-5 animate-rise">
        <div className="flex flex-wrap items-center gap-3 text-sm text-fg-faint">
          <Link to="/runs" className="hover:text-fg">← Runs</Link>
          <span>·</span>
          <span>{formatDate(run.createdAt)}</span>
          <span>{RUN_KIND_LABELS[run.kind]}</span>
          <RunStatusBadge status={run.status} />
        </div>
        <h1 className="max-w-4xl text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
          {run.headline ?? (live ? IN_PROGRESS[run.kind] : "Untitled run")}
        </h1>
        <RunStats run={run} />
      </header>

      {run.error && (
        <p className="rounded-xl border border-danger/20 bg-danger-soft px-4 py-3 font-mono text-xs text-danger">{run.error}</p>
      )}

      <div className="grid items-start gap-10 lg:grid-cols-[minmax(0,1fr)_26rem]">
        <View run={run} live={live} />
        <div className="lg:sticky lg:top-22">
          <RunTrace events={events} live={live} />
        </div>
      </div>
    </div>
  );
}
