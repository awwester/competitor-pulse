import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { useApiMutation } from "@/hooks/useApiMutation";
import type { CompetitorInput, TrackedPageInput } from "@/types/api";

const invalidates = [["competitors"], ["dashboard"]];

export const useCompetitors = () => useQuery({ queryKey: ["competitors"], queryFn: api.competitors });

export const useCreateCompetitor = () =>
  useApiMutation(api.createCompetitor, {
    invalidates,
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
