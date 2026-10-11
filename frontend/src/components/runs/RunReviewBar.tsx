import { Check, X } from "lucide-react";
import { Link } from "react-router";

import { Button } from "@/components/ui/Button";
import { useCanWrite } from "@/hooks/useMeta";
import { useDismissRun, usePublishRun } from "@/hooks/useRuns";
import { useWorkspace } from "@/hooks/useWorkspace";
import type { RunDetail } from "@/types/api";

/** Human-in-the-loop gate: nothing is sent to Slack/email until a person approves. */
export function RunReviewBar({ run }: { run: RunDetail }) {
  const canWrite = useCanWrite();
  const { data: workspace } = useWorkspace();
  const sends = !workspace || workspace.slackConfigured || workspace.notifyEmails.length > 0;
  const publish = usePublishRun(run.id, sends);
  const dismiss = useDismissRun(run.id);
  const kept = run.findings.filter((f) => !f.isDismissed).length;
  const busy = publish.isPending || dismiss.isPending;

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-wait/30 bg-wait-soft px-5 py-4 animate-rise">
      <div>
        <p className="eyebrow text-wait">Awaiting your review</p>
        <p className="mt-1 text-sm text-fg-muted">
          {sends ? (
            <>
              Dismiss any findings that miss the mark, then approve to send{" "}
              <strong className="text-fg">{kept}</strong> finding{kept === 1 ? "" : "s"} to your channels.
            </>
          ) : (
            <>
              Dismiss any findings that miss the mark, then approve. No Slack or email is set up yet,
              so nothing is sent.{" "}
              <Link to="/settings" className="font-medium text-accent hover:underline underline-offset-4">
                Add one in Settings →
              </Link>
            </>
          )}
        </p>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" disabled={!canWrite || busy} onClick={() => dismiss.mutate()}>
          <X className="size-4" /> Dismiss report
        </Button>
        <Button disabled={!canWrite || busy} onClick={() => publish.mutate()}>
          <Check className="size-4" /> {sends ? "Approve & send" : "Approve"}
        </Button>
      </div>
    </div>
  );
}
