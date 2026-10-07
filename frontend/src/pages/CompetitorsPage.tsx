import { Plus } from "lucide-react";
import { useState } from "react";

import { CompetitorCard } from "@/components/competitors/CompetitorCard";
import { CompetitorForm } from "@/components/competitors/CompetitorForm";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useCompetitors, useCreateCompetitor } from "@/hooks/useCompetitors";
import { useCanWrite } from "@/hooks/useMeta";

export function CompetitorsPage() {
  const { data: competitors } = useCompetitors();
  const create = useCreateCompetitor();
  const canWrite = useCanWrite();
  const [adding, setAdding] = useState(false);

  return (
    <>
      <PageHeader eyebrow="Watchlist" title="Competitors">
        {canWrite && !adding && (
          <Button onClick={() => setAdding(true)}>
            <Plus className="size-4" /> Add competitor
          </Button>
        )}
      </PageHeader>

      {adding && (
        <section className="card mb-8 p-6 animate-rise">
          <h2 className="mb-4 text-base font-semibold tracking-tight">New competitor</h2>
          <CompetitorForm
            submitLabel="Start tracking"
            pending={create.isPending}
            onSubmit={(values) => create.mutate(values, { onSuccess: () => setAdding(false) })}
            onCancel={() => setAdding(false)}
          />
        </section>
      )}

      {competitors?.length === 0 && !adding && (
        <EmptyState title="Your watchlist is empty">
          Add a competitor, then the pages that signal strategy: pricing, changelog, homepage, careers.
        </EmptyState>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {competitors?.map((competitor, i) => (
          <CompetitorCard key={competitor.id} competitor={competitor} canWrite={canWrite} index={i} />
        ))}
      </div>
    </>
  );
}
