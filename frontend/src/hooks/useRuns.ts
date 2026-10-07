import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { useApiMutation } from "@/hooks/useApiMutation";
import type { RunStatus } from "@/types/api";

const LIVE_INTERVAL = 2_000;

export const isActive = (status: RunStatus | undefined) =>
  status === "queued" || status === "running";

export const useRuns = () =>
  useQuery({
    queryKey: ["runs"],
    queryFn: api.runs,
    refetchInterval: (query) =>
      query.state.data?.some((run) => isActive(run.status)) ? LIVE_INTERVAL : false,
  });

export const useRun = (id: string) =>
  useQuery({
    queryKey: ["run", id],
    queryFn: () => api.run(id),
    refetchInterval: (query) => (isActive(query.state.data?.status) ? LIVE_INTERVAL : false),
  });

/** Polls while the run is active; keying on status also grabs the final events once it ends. */
export const useRunEvents = (id: string, status: RunStatus | undefined) =>
  useQuery({
    queryKey: ["runEvents", id, status],
    queryFn: () => api.runEvents(id),
    enabled: status !== undefined,
    placeholderData: (previous) => previous,
    refetchInterval: isActive(status) ? LIVE_INTERVAL : false,
  });

export const useCreateRun = () =>
  useApiMutation(api.createRun, {
    invalidates: [["runs"], ["dashboard"]],
    success: "Check queued. The worker will pick it up in a few seconds",
  });

const reviewInvalidates = (id: string) => [["run", id], ["runEvents", id], ["runs"], ["dashboard"]];

export const usePublishRun = (id: string) =>
  useApiMutation(() => api.publishRun(id), {
    invalidates: reviewInvalidates(id),
    success: "Report approved and sent",
  });

export const useDismissRun = (id: string) =>
  useApiMutation(() => api.dismissRun(id), {
    invalidates: reviewInvalidates(id),
    success: "Report dismissed",
  });

export const useToggleFinding = (runId: string) =>
  useApiMutation(
    ({ id, isDismissed }: { id: string; isDismissed: boolean }) =>
      api.updateFinding(id, isDismissed),
    { invalidates: [["run", runId], ["dashboard"]] },
  );
