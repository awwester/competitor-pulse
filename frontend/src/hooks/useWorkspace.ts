import { useQuery } from "@tanstack/react-query";
import { createContext, useContext } from "react";

import { api } from "@/lib/api";
import { useApiMutation } from "@/hooks/useApiMutation";

interface CurrentWorkspace {
  workspaceId: string;
  /** Go to a company's brief, clearing the previous company's cached data if it changes. */
  switchTo: (id: string) => void;
}

export const WorkspaceContext = createContext<CurrentWorkspace | null>(null);

export function useCurrentWorkspace(): CurrentWorkspace {
  const context = useContext(WorkspaceContext);
  if (!context) throw new Error("useCurrentWorkspace must be used inside WorkspaceProvider");
  return context;
}

export const useWorkspaces = () => useQuery({ queryKey: ["workspaces"], queryFn: api.workspaces });

export const useWorkspace = () => useQuery({ queryKey: ["workspace"], queryFn: api.workspace });

export const useCreateWorkspace = () =>
  useApiMutation(api.createWorkspace, { invalidates: [["workspaces"]], success: (w) => `Added ${w.name}` });

export const useUpdateWorkspace = () =>
  useApiMutation(api.updateWorkspace, {
    invalidates: [["workspace"], ["workspaces"]],
    success: "Settings saved",
  });

export const useDeleteWorkspace = () =>
  useApiMutation(api.deleteWorkspace, { invalidates: [["workspaces"]], success: "Company deleted" });
