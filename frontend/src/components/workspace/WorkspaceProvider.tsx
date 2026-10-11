import { useQueryClient } from "@tanstack/react-query";
import { Fragment, useCallback, useMemo, useState, type ReactNode } from "react";
import { useNavigate } from "react-router";

import { AppFrame } from "@/components/layout/AppFrame";
import { WorkspaceContext, useWorkspaces } from "@/hooks/useWorkspace";
import { setWorkspaceId } from "@/lib/api";
import { WelcomePage } from "@/pages/WelcomePage";

const STORAGE_KEY = "competitor-pulse:workspace";
/** Queries that aren't scoped to a company survive a switch. */
const GLOBAL_QUERIES = new Set(["meta", "workspaces"]);

function readSaved(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function save(id: string) {
  try {
    localStorage.setItem(STORAGE_KEY, id);
  } catch {
    // Without storage the choice just lasts until reload.
  }
}

/** Resolves the current company (last used, else the first) before rendering the app, or welcomes a fresh install. */
export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { data: workspaces } = useWorkspaces();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [selected, setSelected] = useState(readSaved);

  const workspaceId = workspaces?.some((w) => w.id === selected) ? selected : workspaces?.[0]?.id;
  if (workspaceId) setWorkspaceId(workspaceId);

  const switchTo = useCallback(
    (id: string | null) => {
      navigate("/");
      if (id === workspaceId) return;
      if (id) {
        setWorkspaceId(id);
        save(id);
      }
      setSelected(id);
      queryClient.removeQueries({ predicate: (q) => !GLOBAL_QUERIES.has(String(q.queryKey[0])) });
    },
    [workspaceId, navigate, queryClient],
  );

  const value = useMemo(() => workspaceId && { workspaceId, switchTo }, [workspaceId, switchTo]);
  if (workspaces?.length === 0) {
    return (
      <AppFrame>
        <WelcomePage />
      </AppFrame>
    );
  }
  if (!value) return null;
  return (
    <WorkspaceContext value={value}>
      {/* Remount on switch so every page refetches for the new company. */}
      <Fragment key={value.workspaceId}>{children}</Fragment>
    </WorkspaceContext>
  );
}
