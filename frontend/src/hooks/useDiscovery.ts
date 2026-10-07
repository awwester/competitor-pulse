import { api } from "@/lib/api";
import { useApiMutation } from "@/hooks/useApiMutation";
import { isActive, useRuns } from "@/hooks/useRuns";
import type { RunSummary, SuggestionInput } from "@/types/api";

/** Queued or running page discoveries, by competitor. Polls while any are active. */
export function useActivePageDiscoveries(): Map<string, RunSummary> {
  const { data: runs = [] } = useRuns();
  return new Map(
    runs
      .filter((r) => r.kind === "page_discovery" && r.competitorId && isActive(r.status))
      .map((r) => [r.competitorId as string, r]),
  );
}

export const useStartDiscovery = () =>
  useApiMutation(api.startDiscovery, {
    invalidates: [["runs"], ["dashboard"], ["workspace"]],
    success: "Discovery started. The agent is reading your site",
  });

export const useDiscoverPages = () =>
  useApiMutation(api.discoverPages, {
    invalidates: [["runs"]],
    success: "Finding pages to track",
  });

export const useToggleSuggestion = (runId: string) =>
  useApiMutation(
    ({ id, isSelected }: { id: string; isSelected: boolean }) => api.updateSuggestion(id, isSelected),
    { invalidates: [["run", runId]] },
  );

export const useAddSuggestion = (runId: string) =>
  useApiMutation((body: SuggestionInput) => api.addSuggestion(runId, body), {
    invalidates: [["run", runId]],
    success: (s) => `Added ${s.name}`,
  });

export const useApplyDiscovery = (runId: string) =>
  useApiMutation(() => api.applyDiscovery(runId), {
    invalidates: [["run", runId], ["runEvents", runId], ["runs"], ["competitors"], ["dashboard"]],
    success: "Competitors added. Finding their pages now",
  });
