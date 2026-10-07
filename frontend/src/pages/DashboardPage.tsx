import { Link } from "react-router";

import { FindingCard } from "@/components/runs/FindingCard";
import { RunNowButton } from "@/components/runs/RunNowButton";
import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Stat } from "@/components/ui/Stat";
import { useDashboard } from "@/hooks/useDashboard";
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
              <h1 className="font-display text-4xl leading-[1.1] text-balance sm:text-5xl">
                {latestRun.headline ?? "A check is in progress…"}
              </h1>
              <div className="mt-6 flex flex-wrap items-center gap-3 font-mono text-xs text-ink-faint">
                <RunStatusBadge status={latestRun.status} />
                <span>{timeAgo(latestRun.createdAt)}</span>
                <Link to={`/runs/${latestRun.id}`} className="text-ink underline decoration-signal underline-offset-4">
                  Read the full report →
                </Link>
              </div>
            </>
          ) : (
            <h1 className="font-display text-4xl leading-[1.08] text-ink-soft italic sm:text-6xl">
              Nothing to report yet.
            </h1>
          )}
        </div>

        <aside className="space-y-6 lg:border-l lg:border-ink lg:pl-8 animate-rise [animation-delay:120ms]">
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
        <div className="flex items-baseline justify-between border-b border-ink pb-3">
          <h2 className="font-display text-2xl">Top signals</h2>
          <span className="eyebrow">Last 30 days · by significance</span>
        </div>
        {data.topFindings.length ? (
          data.topFindings.map((finding, i) => (
            <FindingCard key={finding.id} finding={finding} index={i} showRunLink />
          ))
        ) : (
          <div className="mt-6">
            <EmptyState title="No signals yet">
              {data.competitorCount ? (
                "The first run captures a baseline of each page. Findings appear once something changes."
              ) : (
                <>
                  Start by <Link to="/competitors" className="underline">adding a competitor</Link> and the pages you
                  want watched.
                </>
              )}
            </EmptyState>
          </div>
        )}
      </section>
    </div>
  );
}
