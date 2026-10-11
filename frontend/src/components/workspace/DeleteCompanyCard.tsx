import { useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/Button";
import { useCanWrite } from "@/hooks/useMeta";
import { useCurrentWorkspace, useDeleteWorkspace, useWorkspaces } from "@/hooks/useWorkspace";
import { companyName } from "@/lib/format";
import type { Workspace } from "@/types/api";

export function DeleteCompanyCard({ workspace }: { workspace: Workspace }) {
  const canWrite = useCanWrite();
  const { switchTo } = useCurrentWorkspace();
  const { data: workspaces = [] } = useWorkspaces();
  const queryClient = useQueryClient();
  const remove = useDeleteWorkspace();
  const name = companyName(workspace);
  const next = workspaces.find((w) => w.id !== workspace.id);

  const onDelete = () => {
    if (!confirm(`Delete ${name}? Its competitors, runs and findings will be deleted.`)) return;
    remove.mutate(workspace.id, {
      onSuccess: () => {
        // Drop it from the list now, so the deleted company is never re-selected while it refetches.
        queryClient.setQueryData<Workspace[]>(["workspaces"], (list) => list?.filter((w) => w.id !== workspace.id));
        // With no company left, the welcome screen takes over.
        switchTo(next?.id ?? null);
      },
    });
  };

  return (
    <section className="card space-y-3 p-6 animate-rise [animation-delay:200ms]">
      <h2 className="text-base font-semibold tracking-tight">Delete company</h2>
      <p className="text-sm text-fg-muted">Removes this company with its competitors, runs and findings.</p>
      <Button
        type="button"
        variant="outline"
        disabled={!canWrite || remove.isPending}
        onClick={onDelete}
        className="w-full"
      >
        Delete {name}
      </Button>
    </section>
  );
}
