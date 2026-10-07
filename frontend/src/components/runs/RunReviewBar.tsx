import { Check, X } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useCanWrite } from "@/hooks/useMeta";
import { useDismissRun, usePublishRun } from "@/hooks/useRuns";
import type { RunDetail } from "@/types/api";

/** Human-in-the-loop gate: nothing is sent to Slack/email until a person approves. */
export function RunReviewBar({ run }: { run: RunDetail }) {
  const canWrite = useCanWrite();
  const publish = usePublishRun(run.id);
  const dismiss = useDismissRun(run.id);
  const kept = run.findings.filter((f) => !f.isDismissed).length;
  const busy = publish.isPending || dismiss.isPending;

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 border border-wait/40 bg-wait-soft/60 px-5 py-4 animate-rise">
      <div>
        <p className="eyebrow text-wait">Awaiting your review</p>
        <p className="mt-1 text-sm text-ink-soft">
          Dismiss any findings that miss the mark, then approve to send{" "}
          <strong className="text-ink">{kept}</strong> finding{kept === 1 ? "" : "s"} to your channels.
        </p>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" disabled={!canWrite || busy} onClick={() => dismiss.mutate()}>
          <X className="size-4" /> Dismiss report
        </Button>
        <Button variant="signal" disabled={!canWrite || busy} onClick={() => publish.mutate()}>
          <Check className="size-4" /> Approve &amp; send
        </Button>
      </div>
    </div>
  );
}
