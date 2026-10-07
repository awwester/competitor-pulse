import { Link } from "react-router";

import { OnboardingCard } from "@/components/discovery/OnboardingCard";
import { FindingCard } from "@/components/runs/FindingCard";
import { RunNowButton } from "@/components/runs/RunNowButton";
import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Stat } from "@/components/ui/Stat";
import { useDashboard } from "@/hooks/useDashboard";
import { RUN_KIND_LABELS } from "@/hooks/useRuns";
import { formatUsd, timeAgo } from "@/lib/format";

export function DashboardPage() {
  const { data } = useDashboard();
  if (!data) return null;
  const { latestRun } = data;

  return (
    <div className="space-y-14">
      <section className="grid gap-10 lg:grid-cols-[1fr_18rem]">
        <div className="animate-rise">
          <p className="eyebrow mb-4">The brief</p>
          {latestRun ? (
            <>
              <h1 className="text-3xl font-semibold leading-tight tracking-tight text-balance sm:text-4xl">
                {latestRun.headline ?? `${RUN_KIND_LABELS[latestRun.kind]} in progress…`}
              </h1>
              <div className="mt-5 flex flex-wrap items-center gap-3 text-sm text-fg-faint">
                <RunStatusBadge status={latestRun.status} />
                <span>{timeAgo(latestRun.createdAt)}</span>
                <Link to={`/runs/${latestRun.id}`} className="font-medium text-accent hover:underline underline-offset-4">
                  {latestRun.kind === "check" ? "Read the full report →" : "Open run →"}
                </Link>
              </div>
            </>
          ) : (
            <h1 className="text-3xl font-semibold tracking-tight text-fg-muted sm:text-4xl">
              Nothing to report yet.
            </h1>
          )}
        </div>

        <aside className="card space-y-6 self-start p-6 animate-rise [animation-delay:120ms]">
          <div className="grid grid-cols-2 gap-6">
            <Stat label="Competitors" value={data.competitorCount} />
            <Stat label="Pages" value={data.pageCount} />
            <Stat label="Runs" value={data.runCount} />
            <Stat label="Spend" value={formatUsd(data.totalCostUsd)} />
          </div>
          <RunNowButton />
        </aside>
      </section>

      <section>
        <div className="mb-4 flex items-baseline justify-between">
          <h2 className="text-lg font-semibold tracking-tight">Top signals</h2>
          <span className="eyebrow">Last 30 days · by significance</span>
        </div>
        {data.topFindings.length ? (
          <div className="card divide-y divide-line">
            {data.topFindings.map((finding, i) => (
              <FindingCard key={finding.id} finding={finding} index={i} showRunLink />
            ))}
          </div>
        ) : data.competitorCount ? (
          <EmptyState title="No signals yet">
            The first run captures a baseline of each page. Findings appear once something changes.
          </EmptyState>
        ) : (
          <OnboardingCard />
        )}
      </section>
    </div>
  );
}
