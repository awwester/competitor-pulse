import { cn, humanize } from "@/lib/format";
import type { RunStatus } from "@/types/api";

const STYLES: Record<RunStatus, string> = {
  queued: "bg-paper-deep text-ink-soft",
  running: "bg-ink text-paper",
  awaiting_review: "bg-wait-soft text-wait",
  published: "bg-ok-soft text-ok",
  dismissed: "bg-paper-deep text-ink-faint line-through",
  no_changes: "bg-paper-deep text-ink-soft",
  failed: "bg-signal-soft text-signal",
};

const LABELS: Partial<Record<RunStatus, string>> = { awaiting_review: "needs review" };

export function RunStatusBadge({ status }: { status: RunStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm px-2 py-0.5 font-mono text-[11px] uppercase tracking-wider",
        STYLES[status],
      )}
    >
      {status === "running" && <span className="size-1.5 rounded-full bg-signal animate-pulse" />}
      {LABELS[status] ?? humanize(status)}
    </span>
  );
}
