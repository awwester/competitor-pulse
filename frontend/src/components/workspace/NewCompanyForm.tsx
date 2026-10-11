import { DiscoveryForm } from "@/components/discovery/DiscoveryForm";
import { useCreateWorkspace } from "@/hooks/useWorkspace";
import type { Workspace } from "@/types/api";

/** Adds a company from its website; the API starts discovery, which also names it. */
export function NewCompanyForm({ onCreated }: { onCreated: (workspace: Workspace) => void }) {
  const create = useCreateWorkspace();

  return (
    <DiscoveryForm
      pending={create.isPending}
      onSubmit={(website) => create.mutate({ website }, { onSuccess: onCreated })}
    />
  );
}
