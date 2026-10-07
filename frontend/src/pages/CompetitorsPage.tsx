import { Plus } from "lucide-react";
import { useState } from "react";

import { CompetitorCard } from "@/components/competitors/CompetitorCard";
import { CompetitorForm } from "@/components/competitors/CompetitorForm";
import { DiscoverCompetitorsButton } from "@/components/discovery/DiscoverCompetitorsButton";
import { OnboardingCard } from "@/components/discovery/OnboardingCard";
import { PageDiscoveryProgress } from "@/components/discovery/PageDiscoveryProgress";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { useCompetitors, useCreateCompetitor } from "@/hooks/useCompetitors";
import { useActivePageDiscoveries } from "@/hooks/useDiscovery";
import { useCanWrite } from "@/hooks/useMeta";
import { useWorkspace } from "@/hooks/useWorkspace";

export function CompetitorsPage() {
  const discoveries = useActivePageDiscoveries();
  const { data: competitors } = useCompetitors(discoveries.size > 0);
  const { data: workspace } = useWorkspace();
  const create = useCreateCompetitor();
  const canWrite = useCanWrite();
  const [adding, setAdding] = useState(false);

  return (
    <>
      <PageHeader eyebrow="Watchlist" title="Competitors">
        {workspace?.website && <DiscoverCompetitorsButton website={workspace.website} />}
        {canWrite && !adding && (
          <Button onClick={() => setAdding(true)}>
            <Plus className="size-4" /> Add competitor
          </Button>
        )}
      </PageHeader>

      {adding && (
        <section className="card mb-8 p-6 animate-rise">
          <h2 className="text-base font-semibold tracking-tight">New competitor</h2>
          <p className="mb-4 mt-1 text-sm text-fg-muted">
            The agent finds the pages worth watching on their site. You can add or remove pages after.
          </p>
          <CompetitorForm
            submitLabel="Start tracking"
            pending={create.isPending}
            onSubmit={(values) => create.mutate(values, { onSuccess: () => setAdding(false) })}
            onCancel={() => setAdding(false)}
          />
        </section>
      )}

      {competitors?.length === 0 && !adding && <OnboardingCard manualLink={false} />}

      <div className="mb-8 empty:hidden">
        <PageDiscoveryProgress />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {competitors?.map((competitor, i) => (
          <CompetitorCard
            key={competitor.id}
            competitor={competitor}
            canWrite={canWrite}
            discovery={discoveries.get(competitor.id)}
            index={i}
          />
        ))}
      </div>
    </>
  );
}
