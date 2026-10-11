import { useState } from "react";

import { RunNowButton } from "@/components/runs/RunNowButton";
import { RunRow } from "@/components/runs/RunRow";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { useRuns } from "@/hooks/useRuns";
import type { RunSummary } from "@/types/api";

type RunFilter = "all" | "checks" | "setup";

const FILTERS: { value: RunFilter; label: string; matches: (run: RunSummary) => boolean }[] = [
  { value: "all", label: "All", matches: () => true },
  { value: "checks", label: "Checks", matches: (run) => run.kind === "check" },
  { value: "setup", label: "Setup", matches: (run) => run.kind !== "check" },
];

export function RunsPage() {
  const { data: runs } = useRuns();
  const [filter, setFilter] = useState<RunFilter>("all");
  const shown = runs?.filter(FILTERS.find((f) => f.value === filter)!.matches) ?? [];

  return (
    <>
      <PageHeader eyebrow="Archive" title="Runs">
        <RunNowButton />
      </PageHeader>
      {runs?.length === 0 && (
        <EmptyState title="No runs yet">
          Once competitors are tracked, checks run on a schedule or whenever you start one.
        </EmptyState>
      )}
      {runs?.length ? (
        <div className="space-y-4">
          <SegmentedControl
            label="Filter runs"
            value={filter}
            onChange={setFilter}
            options={FILTERS.map(({ value, label, matches }) => ({ value, label, count: runs.filter(matches).length }))}
          />
          {shown.length ? (
            <div className="card divide-y divide-line overflow-hidden">
              {shown.map((run) => <RunRow key={run.id} run={run} />)}
            </div>
          ) : (
            <EmptyState title="No runs here yet" />
          )}
        </div>
      ) : null}
    </>
  );
}
