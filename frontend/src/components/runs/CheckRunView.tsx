import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { FindingCard } from "@/components/runs/FindingCard";
import { RunReviewBar } from "@/components/runs/RunReviewBar";
import { EmptyState } from "@/components/ui/EmptyState";
import { useCanWrite } from "@/hooks/useMeta";
import { useToggleFinding } from "@/hooks/useRuns";
import type { RunDetail } from "@/types/api";

export function CheckRunView({ run, live }: { run: RunDetail; live: boolean }) {
  const toggleFinding = useToggleFinding(run.id);
  const canWrite = useCanWrite();
  const reviewing = run.status === "awaiting_review";

  return (
    <div className="space-y-12">
      {reviewing && <RunReviewBar run={run} />}

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
  );
}
