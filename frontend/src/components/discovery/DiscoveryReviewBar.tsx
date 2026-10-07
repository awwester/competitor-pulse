import { Check, X } from "lucide-react";
import { useNavigate } from "react-router";

import { Button } from "@/components/ui/Button";
import { useApplyDiscovery } from "@/hooks/useDiscovery";
import { useCanWrite } from "@/hooks/useMeta";
import { useDismissRun } from "@/hooks/useRuns";
import type { RunDetail } from "@/types/api";

/** Human-in-the-loop gate: no competitor is tracked until a person approves the shortlist. */
export function DiscoveryReviewBar({ run }: { run: RunDetail }) {
  const canWrite = useCanWrite();
  const navigate = useNavigate();
  const apply = useApplyDiscovery(run.id);
  const dismiss = useDismissRun(run.id);
  const selected = run.suggestions.filter((s) => s.isSelected).length;
  const busy = apply.isPending || dismiss.isPending;

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-wait/30 bg-wait-soft px-5 py-4 animate-rise">
      <div>
        <p className="eyebrow text-wait">Awaiting your review</p>
        <p className="mt-1 text-sm text-fg-muted">
          Untick competitors that don't belong and add any that are missing. The agent then finds
          the pages worth watching on each one.
        </p>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" disabled={!canWrite || busy} onClick={() => dismiss.mutate()}>
          <X className="size-4" /> Dismiss
        </Button>
        <Button disabled={!canWrite || busy || !selected} onClick={() => apply.mutate(undefined, { onSuccess: () => navigate("/competitors") })}>
          <Check className="size-4" /> Track {selected} competitor{selected === 1 ? "" : "s"}
        </Button>
      </div>
    </div>
  );
}
