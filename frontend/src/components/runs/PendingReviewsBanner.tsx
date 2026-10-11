import { Link } from "react-router";

import { RUN_KIND_LABELS } from "@/hooks/useRuns";
import { timeAgo } from "@/lib/format";
import type { RunSummary } from "@/types/api";

/** Runs held at the human-in-the-loop gate, so they can't get buried under newer runs. */
export function PendingReviewsBanner({ runs }: { runs: RunSummary[] }) {
  return (
    <section className="rounded-xl border border-wait/30 bg-wait-soft px-5 py-4 animate-rise">
      <p className="eyebrow text-wait">{runs.length} awaiting your review</p>
      <ul className="mt-2 divide-y divide-wait/15">
        {runs.map((run) => (
          <li key={run.id}>
            <Link
              to={`/runs/${run.id}`}
              className="group flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-2"
            >
              <span className="min-w-0 text-sm font-medium group-hover:text-wait">
                {run.headline ?? RUN_KIND_LABELS[run.kind]}
              </span>
              <span className="text-xs text-fg-muted">
                {RUN_KIND_LABELS[run.kind]} · {timeAgo(run.createdAt)} ·{" "}
                <span className="font-medium text-wait">Review →</span>
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
