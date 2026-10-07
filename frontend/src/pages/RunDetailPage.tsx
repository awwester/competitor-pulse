import ReactMarkdown from "react-markdown";
import { Link, useParams } from "react-router";
import remarkGfm from "remark-gfm";

import { FindingCard } from "@/components/runs/FindingCard";
import { RunReviewBar } from "@/components/runs/RunReviewBar";
import { RunStats } from "@/components/runs/RunStats";
import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { RunTrace } from "@/components/runs/RunTrace";
import { EmptyState } from "@/components/ui/EmptyState";
import { useCanWrite } from "@/hooks/useMeta";
import { isActive, useRun, useRunEvents, useToggleFinding } from "@/hooks/useRuns";
import { formatDate } from "@/lib/format";

export function RunDetailPage() {
  const { runId = "" } = useParams();
  const { data: run } = useRun(runId);
  const live = isActive(run?.status);
  const { data: events = [] } = useRunEvents(runId, run?.status);
  const toggleFinding = useToggleFinding(runId);
  const canWrite = useCanWrite();

  if (!run) return null;
  const reviewing = run.status === "awaiting_review";

  return (
    <div className="space-y-10">
      <header className="space-y-5 border-b border-ink pb-8 animate-rise">
        <div className="flex flex-wrap items-center gap-3 font-mono text-xs text-ink-faint">
          <Link to="/runs" className="hover:text-ink">← Runs</Link>
          <span>·</span>
          <span>{formatDate(run.createdAt)}</span>
          <span className="uppercase tracking-wider">{run.trigger}</span>
          <RunStatusBadge status={run.status} />
        </div>
        <h1 className="max-w-4xl font-display text-4xl leading-[1.08] sm:text-5xl">
          {run.headline ?? (live ? "Checking competitors…" : "Untitled run")}
        </h1>
        <RunStats run={run} />
      </header>

      {reviewing && <RunReviewBar run={run} />}
      {run.error && (
        <p className="border-l-2 border-signal bg-signal-soft/50 px-4 py-3 font-mono text-xs text-signal">{run.error}</p>
      )}

      <div className="grid items-start gap-10 lg:grid-cols-[minmax(0,1fr)_26rem]">
        <div className="space-y-12">
          <section>
            <div className="flex items-baseline justify-between border-b border-ink pb-3">
              <h2 className="font-display text-2xl">Findings</h2>
              <span className="eyebrow">{run.findings.length} recorded</span>
            </div>
            {run.findings.map((finding, i) => (
              <FindingCard
                key={finding.id}
                finding={finding}
                index={i}
                onToggleDismissed={
                  reviewing && canWrite
                    ? (f) => toggleFinding.mutate({ id: f.id, isDismissed: !f.isDismissed })
                    : undefined
                }
              />
            ))}
            {run.findings.length === 0 && !live && (
              <div className="mt-6">
                <EmptyState title="Nothing significant">
                  {run.pagesChanged
                    ? "Pages changed, but the agent judged every change to be noise."
                    : "No tracked pages changed since the last check."}
                </EmptyState>
              </div>
            )}
          </section>

          {run.reportMarkdown && (
            <section>
              <h2 className="border-b border-ink pb-3 font-display text-2xl">Analyst report</h2>
              <article className="prose prose-stone mt-6 max-w-none prose-headings:font-display prose-headings:font-normal prose-a:decoration-signal">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{run.reportMarkdown}</ReactMarkdown>
              </article>
            </section>
          )}
        </div>

        <div className="lg:sticky lg:top-6">
          <RunTrace events={events} live={live} />
        </div>
      </div>
    </div>
  );
}
