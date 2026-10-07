import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { api } from "@/lib/api";
import { useApiMutation } from "@/hooks/useApiMutation";
import { LIVE_INTERVAL } from "@/hooks/useRuns";
import type { CompetitorInput, TrackedPageInput } from "@/types/api";

const invalidates = [["competitors"], ["dashboard"]];

/** `live` polls while a page discovery may be adding pages. */
export function useCompetitors(live = false) {
  const queryClient = useQueryClient();
  const wasLive = useRef(live);
  useEffect(() => {
    // Fetch once more when polling stops, so pages added just before the run ended show up.
    if (wasLive.current && !live) queryClient.invalidateQueries({ queryKey: ["competitors"] });
    wasLive.current = live;
  }, [live, queryClient]);
  return useQuery({
    queryKey: ["competitors"],
    queryFn: api.competitors,
    refetchInterval: live ? LIVE_INTERVAL : false,
  });
}

export const useCreateCompetitor = () =>
  useApiMutation(api.createCompetitor, {
    // Without pages, creating a competitor also queues a page discovery run.
    invalidates: [...invalidates, ["runs"]],
    success: (c) => `Now tracking ${c.name}`,
  });

export const useUpdateCompetitor = (id: string) =>
  useApiMutation((body: Partial<CompetitorInput>) => api.updateCompetitor(id, body), {
    invalidates,
    success: "Competitor updated",
  });

export const useDeleteCompetitor = () =>
  useApiMutation(api.deleteCompetitor, { invalidates, success: "Competitor removed" });

export const useAddPage = (competitorId: string) =>
  useApiMutation((body: TrackedPageInput) => api.addPage(competitorId, body), {
    invalidates,
    success: "Page added",
  });

export const useUpdatePage = () =>
  useApiMutation(
    ({ id, ...body }: { id: string } & Partial<TrackedPageInput>) => api.updatePage(id, body),
    { invalidates },
  );

export const useDeletePage = () => useApiMutation(api.deletePage, { invalidates });
