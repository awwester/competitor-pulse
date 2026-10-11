import { DiscoveryForm } from "@/components/discovery/DiscoveryForm";
import { PageHeader } from "@/components/ui/PageHeader";
import { useCreateWorkspace, useCurrentWorkspace } from "@/hooks/useWorkspace";

export function NewCompanyPage() {
  const create = useCreateWorkspace();
  const { switchTo } = useCurrentWorkspace();

  return (
    <>
      <PageHeader eyebrow="Companies" title="Add a company" />
      <section className="card max-w-xl space-y-6 p-6 animate-rise">
        <p className="text-sm text-fg-muted">
          Each company has its own profile, competitors, runs and delivery settings. Enter its
          website and the agent fills in the rest, starting with a shortlist of competitors for you
          to approve.
        </p>
        {/* The new company's brief follows the discovery this starts. */}
        <DiscoveryForm
          pending={create.isPending}
          onSubmit={(website) => create.mutate({ website }, { onSuccess: (workspace) => switchTo(workspace.id) })}
        />
      </section>
    </>
  );
}
