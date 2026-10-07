import { Pencil, Sparkles, Trash2 } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router";

import { AddPageForm } from "@/components/competitors/AddPageForm";
import { CompetitorForm } from "@/components/competitors/CompetitorForm";
import { PageRow } from "@/components/competitors/PageRow";
import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { Button } from "@/components/ui/Button";
import { useDeleteCompetitor, useUpdateCompetitor } from "@/hooks/useCompetitors";
import { useDiscoverPages } from "@/hooks/useDiscovery";
import type { Competitor, RunSummary } from "@/types/api";

interface CompetitorCardProps {
  competitor: Competitor;
  canWrite: boolean;
  /** The queued or running page discovery for this competitor, if any. */
  discovery?: RunSummary;
  index: number;
}

export function CompetitorCard({ competitor, canWrite, discovery, index }: CompetitorCardProps) {
  const [editing, setEditing] = useState(false);
  const update = useUpdateCompetitor(competitor.id);
  const remove = useDeleteCompetitor();
  const discoverPages = useDiscoverPages();

  const confirmDelete = () => {
    if (confirm(`Stop tracking ${competitor.name}? Its history and findings will be deleted.`)) {
      remove.mutate(competitor.id);
    }
  };

  return (
    <article className="card p-6 animate-rise" style={{ animationDelay: `${index * 70}ms` }}>
      {editing ? (
        <CompetitorForm
          initial={{ name: competitor.name, website: competitor.website, notes: competitor.notes }}
          submitLabel="Save"
          pending={update.isPending}
          onSubmit={(values) => update.mutate(values, { onSuccess: () => setEditing(false) })}
          onCancel={() => setEditing(false)}
        />
      ) : (
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold tracking-tight">{competitor.name}</h2>
            <a href={competitor.website} target="_blank" rel="noreferrer" className="text-sm text-fg-faint hover:text-accent">
              {competitor.website}
            </a>
            {competitor.notes && <p className="mt-2 max-w-prose text-sm text-fg-muted">{competitor.notes}</p>}
            {discovery && (
              <Link
                to={`/runs/${discovery.id}`}
                className="mt-3 flex items-center gap-2 text-xs text-fg-muted hover:text-accent"
              >
                <RunStatusBadge status={discovery.status} />
                {discovery.status === "queued" ? "Waiting to find pages" : "Finding pages"} · watch →
              </Link>
            )}
          </div>
          {canWrite && (
            <div className="flex gap-1">
              <Button variant="ghost" size="sm" onClick={() => setEditing(true)}>
                <Pencil className="size-3.5" /> Edit
              </Button>
              <Button variant="ghost" size="sm" onClick={confirmDelete}>
                <Trash2 className="size-3.5" /> Remove
              </Button>
            </div>
          )}
        </div>
      )}

      <ul className="mt-5 divide-y divide-line rounded-lg border border-line">
        {competitor.pages.map((page) => (
          <PageRow key={page.id} page={page} canWrite={canWrite} />
        ))}
        {competitor.pages.length === 0 && (
          <li className="flex flex-wrap items-center justify-between gap-2 px-3 py-3 text-sm text-fg-faint">
            {discovery ? "Pages will appear here as the agent finds them." : "No pages tracked yet."}
            {canWrite && !discovery && (
              <Button
                variant="outline"
                size="sm"
                disabled={discoverPages.isPending}
                onClick={() => discoverPages.mutate(competitor.id)}
              >
                <Sparkles className="size-3.5" /> Find pages
              </Button>
            )}
          </li>
        )}
      </ul>
      {canWrite && <AddPageForm competitorId={competitor.id} />}
    </article>
  );
}
