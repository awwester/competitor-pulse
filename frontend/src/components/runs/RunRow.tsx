import { Link } from "react-router";

import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { RUN_KIND_LABELS } from "@/hooks/useRuns";
import { formatDate, formatUsd } from "@/lib/format";
import type { RunSummary } from "@/types/api";

export function RunRow({ run }: { run: RunSummary }) {
  return (
    <Link
      to={`/runs/${run.id}`}
      className="group grid grid-cols-[1fr_auto] items-center gap-x-6 gap-y-2 px-5 py-4 transition-colors hover:bg-subtle sm:grid-cols-[10rem_1fr_auto]"
    >
      <div className="text-xs text-fg-faint">
        {formatDate(run.createdAt)}
        <span className="block capitalize">
          {run.kind === "check" ? run.trigger : RUN_KIND_LABELS[run.kind]}
        </span>
      </div>
      <p className="order-last col-span-2 text-[15px] font-medium leading-snug group-hover:text-accent sm:order-none sm:col-span-1">
        {run.headline ?? <span className="text-fg-faint">In progress…</span>}
      </p>
      <div className="flex items-center gap-4 justify-self-end">
        <span className="hidden text-xs tabular-nums text-fg-faint sm:inline">
          {run.kind === "check" && `${run.pagesChanged}/${run.pagesChecked} changed · `}
          {formatUsd(run.costUsd)}
        </span>
        <RunStatusBadge status={run.status} />
      </div>
    </Link>
  );
}
