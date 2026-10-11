import { useQuery } from "@tanstack/react-query";
import { createContext, useContext } from "react";

import { api } from "@/lib/api";
import { useApiMutation } from "@/hooks/useApiMutation";
import { LIVE_INTERVAL } from "@/hooks/useRuns";

interface CurrentWorkspace {
  workspaceId: string;
  /**
   * Go to a company's brief, clearing the previous company's cached data if it changes.
   * `null` drops the selection, e.g. after deleting the last company.
   */
  switchTo: (id: string | null) => void;
}

export const WorkspaceContext = createContext<CurrentWorkspace | null>(null);

export function useCurrentWorkspace(): CurrentWorkspace {
  const context = useContext(WorkspaceContext);
  if (!context) throw new Error("useCurrentWorkspace must be used inside WorkspaceProvider");
  return context;
}

/** `live` polls, e.g. while discovery names the company and writes its profile mid-run. */
export const useWorkspaces = (live = false) =>
  useQuery({ queryKey: ["workspaces"], queryFn: api.workspaces, refetchInterval: live ? LIVE_INTERVAL : false });

export const useWorkspace = (live = false) =>
  useQuery({ queryKey: ["workspace"], queryFn: api.workspace, refetchInterval: live ? LIVE_INTERVAL : false });

export const useCreateWorkspace = () =>
  useApiMutation(api.createWorkspace, {
    invalidates: [["workspaces"]],
    success: "Company added. The agent is reading its site",
  });

export const useUpdateWorkspace = () =>
  useApiMutation(api.updateWorkspace, {
    invalidates: [["workspace"], ["workspaces"]],
    success: "Settings saved",
  });

export const useDeleteWorkspace = () =>
  useApiMutation(api.deleteWorkspace, { invalidates: [["workspaces"]], success: "Company deleted" });
