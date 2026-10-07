import { Pencil, Trash2 } from "lucide-react";
import { useState } from "react";

import { AddPageForm } from "@/components/competitors/AddPageForm";
import { CompetitorForm } from "@/components/competitors/CompetitorForm";
import { PageRow } from "@/components/competitors/PageRow";
import { Button } from "@/components/ui/Button";
import { useDeleteCompetitor, useUpdateCompetitor } from "@/hooks/useCompetitors";
import type { Competitor } from "@/types/api";

export function CompetitorCard({ competitor, canWrite, index }: { competitor: Competitor; canWrite: boolean; index: number }) {
  const [editing, setEditing] = useState(false);
  const update = useUpdateCompetitor(competitor.id);
  const remove = useDeleteCompetitor();

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
          <li className="px-3 py-3 text-sm text-fg-faint">No pages tracked yet.</li>
        )}
      </ul>
      {canWrite && <AddPageForm competitorId={competitor.id} />}
    </article>
  );
}
