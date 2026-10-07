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
    <article className="border-t-2 border-ink pt-5 animate-rise" style={{ animationDelay: `${index * 70}ms` }}>
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
            <h2 className="font-display text-3xl">{competitor.name}</h2>
            <a href={competitor.website} target="_blank" rel="noreferrer" className="font-mono text-xs text-ink-faint hover:text-ink">
              {competitor.website}
            </a>
            {competitor.notes && <p className="mt-2 max-w-prose text-sm text-ink-soft">{competitor.notes}</p>}
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

      <ul className="mt-4">
        {competitor.pages.map((page) => (
          <PageRow key={page.id} page={page} canWrite={canWrite} />
        ))}
        {competitor.pages.length === 0 && (
          <li className="border-t border-rule/70 py-3 text-sm italic text-ink-faint">No pages tracked yet.</li>
        )}
      </ul>
      {canWrite && <AddPageForm competitorId={competitor.id} />}
    </article>
  );
}
