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
      <header className="space-y-5 animate-rise">
        <div className="flex flex-wrap items-center gap-3 text-sm text-fg-faint">
          <Link to="/runs" className="hover:text-fg">← Runs</Link>
          <span>·</span>
          <span>{formatDate(run.createdAt)}</span>
          <span className="capitalize">{run.trigger}</span>
          <RunStatusBadge status={run.status} />
        </div>
        <h1 className="max-w-4xl text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
          {run.headline ?? (live ? "Checking competitors…" : "Untitled run")}
        </h1>
        <RunStats run={run} />
      </header>

      {reviewing && <RunReviewBar run={run} />}
      {run.error && (
        <p className="rounded-xl border border-danger/20 bg-danger-soft px-4 py-3 font-mono text-xs text-danger">{run.error}</p>
      )}

      <div className="grid items-start gap-10 lg:grid-cols-[minmax(0,1fr)_26rem]">
        <div className="space-y-12">
          <section>
            <div className="mb-4 flex items-baseline justify-between">
              <h2 className="text-lg font-semibold tracking-tight">Findings</h2>
              <span className="eyebrow">{run.findings.length} recorded</span>
            </div>
            {run.findings.length > 0 && (
              <div className="card divide-y divide-line">
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
              </div>
            )}
            {run.findings.length === 0 && !live && (
              <EmptyState title="Nothing significant">
                {run.pagesChanged
                  ? "Pages changed, but the agent judged every change to be noise."
                  : "No tracked pages changed since the last check."}
              </EmptyState>
            )}
          </section>

          {run.reportMarkdown && (
            <section>
              <h2 className="mb-4 text-lg font-semibold tracking-tight">Analyst report</h2>
              <article className="card prose prose-slate max-w-none p-6 prose-headings:tracking-tight prose-a:text-accent sm:p-8">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{run.reportMarkdown}</ReactMarkdown>
              </article>
            </section>
          )}
        </div>

        <div className="lg:sticky lg:top-22">
          <RunTrace events={events} live={live} />
        </div>
      </div>
    </div>
  );
}
