import { Link } from "react-router";

import { OnboardingCard } from "@/components/discovery/OnboardingCard";
import { FindingCard } from "@/components/runs/FindingCard";
import { PendingReviewsBanner } from "@/components/runs/PendingReviewsBanner";
import { RunNowButton } from "@/components/runs/RunNowButton";
import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Stat } from "@/components/ui/Stat";
import { useDashboard } from "@/hooks/useDashboard";
import { useMeta } from "@/hooks/useMeta";
import { isActive, RUN_KIND_LABELS, useRuns } from "@/hooks/useRuns";
import { useWorkspace } from "@/hooks/useWorkspace";
import { formatUsd, formatWeekdayTime, timeAgo } from "@/lib/format";

export function DashboardPage() {
  const { data } = useDashboard();
  const { data: meta } = useMeta();
  const { data: runs } = useRuns();
  const { data: workspace } = useWorkspace();
  if (!data) return null;
  // Until a competitor is tracked there's nothing to brief on, so setup is the whole page.
  if (!data.competitorCount) return <OnboardingCard />;
  const { latestCheck, pendingReviews } = data;
  const heroRun = latestCheck ?? runs?.find((run) => isActive(run.status));
  const usingSampleSites =
    !!meta?.sampleCompanyUrl && workspace?.website === meta.sampleCompanyUrl && latestCheck?.status === "no_changes";

  return (
    <div className="space-y-14">
      {pendingReviews.length > 0 && <PendingReviewsBanner runs={pendingReviews} />}

      <section className="grid gap-10 lg:grid-cols-[1fr_18rem]">
        <div className="animate-rise">
          <p className="eyebrow mb-4">The brief</p>
          {heroRun ? (
            <>
              <h1 className="text-3xl font-semibold leading-tight tracking-tight text-balance sm:text-4xl">
                {heroRun.headline ?? `${RUN_KIND_LABELS[heroRun.kind]} in progress…`}
              </h1>
              <div className="mt-5 flex flex-wrap items-center gap-3 text-sm text-fg-faint">
                <RunStatusBadge status={heroRun.status} />
                <span>{timeAgo(heroRun.createdAt)}</span>
                <Link to={`/runs/${heroRun.id}`} className="font-medium text-accent hover:underline underline-offset-4">
                  {heroRun.kind === "check" ? "Read the full report →" : "Watch it run →"}
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
        ) : (
          <EmptyState title="No signals yet">
            The first check captures a baseline of each page. Findings appear once something changes.
            {meta?.nextCheckAt && <> Next check: {formatWeekdayTime(meta.nextCheckAt)}.</>}
            {usingSampleSites && (
              <span className="mt-3 block">
                Watching the sample sites? Run <code className="font-mono text-fg">make demo-advance</code> to
                publish their changes, then run a check now.
              </span>
            )}
          </EmptyState>
        )}
      </section>
    </div>
  );
}
