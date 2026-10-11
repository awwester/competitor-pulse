import { Button } from "@/components/ui/Button";
import { useCanWrite } from "@/hooks/useMeta";
import { useCurrentWorkspace, useDeleteWorkspace, useWorkspaces } from "@/hooks/useWorkspace";
import type { Workspace } from "@/types/api";

export function DeleteCompanyCard({ workspace }: { workspace: Workspace }) {
  const canWrite = useCanWrite();
  const { switchTo } = useCurrentWorkspace();
  const { data: workspaces = [] } = useWorkspaces();
  const remove = useDeleteWorkspace();
  const next = workspaces.find((w) => w.id !== workspace.id);

  const onDelete = () => {
    if (next && confirm(`Delete ${workspace.name}? Its competitors, runs and findings will be deleted.`)) {
      remove.mutate(workspace.id, { onSuccess: () => switchTo(next.id) });
    }
  };

  return (
    <section className="card space-y-3 p-6 animate-rise [animation-delay:200ms]">
      <h2 className="text-base font-semibold tracking-tight">Delete company</h2>
      <p className="text-sm text-fg-muted">
        {next
          ? "Removes this company with its competitors, runs and findings."
          : "This is your only company. Add another before deleting it."}
      </p>
      <Button
        type="button"
        variant="outline"
        disabled={!canWrite || !next || remove.isPending}
        onClick={onDelete}
        className="w-full"
      >
        Delete {workspace.name}
      </Button>
    </section>
  );
}
