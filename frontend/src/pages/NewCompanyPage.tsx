import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Field, Input } from "@/components/ui/Field";
import { PageHeader } from "@/components/ui/PageHeader";
import { useCanWrite } from "@/hooks/useMeta";
import { useCreateWorkspace, useCurrentWorkspace } from "@/hooks/useWorkspace";

export function NewCompanyPage() {
  const canWrite = useCanWrite();
  const create = useCreateWorkspace();
  const { switchTo } = useCurrentWorkspace();
  const [name, setName] = useState("");
  const [website, setWebsite] = useState("");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    // The brief of a company with no competitors offers discovery from this website.
    create.mutate({ name, website }, { onSuccess: (workspace) => switchTo(workspace.id) });
  };

  return (
    <>
      <PageHeader eyebrow="Companies" title="Add a company" />
      <form onSubmit={submit} className="card max-w-xl space-y-6 p-6 animate-rise">
        <p className="text-sm text-fg-muted">
          Each company has its own profile, competitors, runs and delivery settings.
        </p>
        <Field label="Company name">
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </Field>
        <Field label="Website" hint="Competitor discovery starts from this site.">
          <Input
            required
            type="url"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            placeholder="https://yourcompany.com"
          />
        </Field>
        <Button type="submit" disabled={!canWrite || create.isPending}>
          Add company
        </Button>
      </form>
    </>
  );
}
