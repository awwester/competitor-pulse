import { PageHeader } from "@/components/ui/PageHeader";
import { NewCompanyForm } from "@/components/workspace/NewCompanyForm";
import { useCurrentWorkspace } from "@/hooks/useWorkspace";

export function NewCompanyPage() {
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
        <NewCompanyForm onCreated={(workspace) => switchTo(workspace.id)} />
      </section>
    </>
  );
}
