import { Link } from "react-router";

import { AddSuggestionForm } from "@/components/discovery/AddSuggestionForm";
import { DiscoveryReviewBar } from "@/components/discovery/DiscoveryReviewBar";
import { PageDiscoveryProgress } from "@/components/discovery/PageDiscoveryProgress";
import { SuggestionRow } from "@/components/discovery/SuggestionRow";
import { EmptyState } from "@/components/ui/EmptyState";
import { useToggleSuggestion } from "@/hooks/useDiscovery";
import { useCanWrite } from "@/hooks/useMeta";
import { useWorkspace } from "@/hooks/useWorkspace";
import type { RunDetail } from "@/types/api";

export function CompanyDiscoveryView({ run, live }: { run: RunDetail; live: boolean }) {
  const canWrite = useCanWrite();
  const { data: workspace } = useWorkspace();
  const toggle = useToggleSuggestion(run.id);
  const reviewing = run.status === "awaiting_review";
  const editable = reviewing && canWrite;

  return (
    <div className="space-y-12">
      {reviewing && <DiscoveryReviewBar run={run} />}
      {run.status === "applied" && (
        <div className="space-y-4">
          <PageDiscoveryProgress />
          <p className="text-sm text-fg-muted">
            You approved {run.suggestions.filter((s) => s.isSelected).length} competitors.{" "}
            <Link to="/competitors" className="font-medium text-accent hover:underline underline-offset-4">
              See them on Competitors →
            </Link>
          </p>
        </div>
      )}

      <section>
        <div className="mb-4 flex items-baseline justify-between">
          <h2 className="text-lg font-semibold tracking-tight">Suggested competitors</h2>
          <span className="eyebrow">{run.suggestions.length} found</span>
        </div>
        {run.suggestions.length > 0 || editable ? (
          <div className="card overflow-hidden">
            <ul className="divide-y divide-line">
              {run.suggestions.map((suggestion) => (
                <SuggestionRow
                  key={suggestion.id}
                  suggestion={suggestion}
                  onToggle={
                    editable ? (s) => toggle.mutate({ id: s.id, isSelected: !s.isSelected }) : undefined
                  }
                />
              ))}
            </ul>
            {editable && <AddSuggestionForm runId={run.id} />}
          </div>
        ) : (
          !live && <EmptyState title="No competitors suggested" />
        )}
      </section>

      {workspace?.companyProfile && (
        <section>
          <div className="mb-4 flex items-baseline justify-between">
            <h2 className="text-lg font-semibold tracking-tight">Company profile</h2>
            <Link to="/settings" className="text-xs font-medium text-accent hover:underline underline-offset-4">
              Edit in settings →
            </Link>
          </div>
          <p className="card whitespace-pre-line p-6 text-[15px] leading-relaxed text-fg-muted">
            {workspace.companyProfile}
          </p>
        </section>
      )}
    </div>
  );
}
