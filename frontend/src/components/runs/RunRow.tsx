import { Link } from "react-router";

import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { formatDate, formatUsd } from "@/lib/format";
import type { RunSummary } from "@/types/api";

export function RunRow({ run }: { run: RunSummary }) {
  return (
    <Link
      to={`/runs/${run.id}`}
      className="group grid grid-cols-[1fr_auto] items-center gap-x-6 gap-y-2 border-t border-rule py-5 transition-colors hover:bg-white/40 sm:grid-cols-[10rem_1fr_auto]"
    >
      <div className="font-mono text-xs text-ink-faint">
        {formatDate(run.createdAt)}
        <span className="block uppercase tracking-wider">{run.trigger}</span>
      </div>
      <p className="order-last col-span-2 font-display text-xl leading-snug group-hover:underline group-hover:decoration-signal group-hover:underline-offset-4 sm:order-none sm:col-span-1">
        {run.headline ?? <span className="italic text-ink-faint">In progress…</span>}
      </p>
      <div className="flex items-center gap-4 justify-self-end">
        <span className="hidden font-mono text-xs tabular-nums text-ink-faint sm:inline">
          {run.pagesChanged}/{run.pagesChecked} changed · {formatUsd(run.costUsd)}
        </span>
        <RunStatusBadge status={run.status} />
      </div>
    </Link>
  );
}
