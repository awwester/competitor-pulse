import { RunNowButton } from "@/components/runs/RunNowButton";
import { RunRow } from "@/components/runs/RunRow";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useRuns } from "@/hooks/useRuns";

export function RunsPage() {
  const { data: runs } = useRuns();

  return (
    <>
      <PageHeader eyebrow="Archive" title="Runs">
        <RunNowButton />
      </PageHeader>
      {runs?.length === 0 && (
        <EmptyState title="No runs yet">Runs happen on schedule, or start one now.</EmptyState>
      )}
      {runs?.length ? (
        <div className="card divide-y divide-line overflow-hidden">
          {runs.map((run) => <RunRow key={run.id} run={run} />)}
        </div>
      ) : null}
    </>
  );
}
