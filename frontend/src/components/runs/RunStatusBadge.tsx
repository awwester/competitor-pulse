import { cn, humanize } from "@/lib/format";
import type { RunStatus } from "@/types/api";

const STYLES: Record<RunStatus, string> = {
  queued: "bg-subtle text-fg-muted ring-line",
  running: "bg-accent-soft text-accent ring-accent/20",
  awaiting_review: "bg-wait-soft text-wait ring-wait/20",
  published: "bg-ok-soft text-ok ring-ok/20",
  applied: "bg-ok-soft text-ok ring-ok/20",
  dismissed: "bg-subtle text-fg-faint ring-line line-through",
  no_changes: "bg-subtle text-fg-muted ring-line",
  completed: "bg-ok-soft text-ok ring-ok/20",
  failed: "bg-danger-soft text-danger ring-danger/20",
};

const LABELS: Partial<Record<RunStatus, string>> = { awaiting_review: "needs review" };

export function RunStatusBadge({ status }: { status: RunStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        STYLES[status],
      )}
    >
      {status === "running" && <span className="size-1.5 rounded-full bg-accent animate-pulse" />}
      {LABELS[status] ?? humanize(status)}
    </span>
  );
}
