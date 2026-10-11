import { useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { DeleteCompanyCard } from "@/components/workspace/DeleteCompanyCard";
import { Field, Input, Textarea, UrlInput } from "@/components/ui/Field";
import { PageHeader } from "@/components/ui/PageHeader";
import { useCanWrite } from "@/hooks/useMeta";
import { useUpdateWorkspace, useWorkspace } from "@/hooks/useWorkspace";
import type { Workspace, WorkspaceUpdate } from "@/types/api";

function SettingsForm({ workspace }: { workspace: Workspace }) {
  const canWrite = useCanWrite();
  const update = useUpdateWorkspace();
  const queryClient = useQueryClient();
  const [name, setName] = useState(workspace.name);
  const [website, setWebsite] = useState(workspace.website ?? "");
  const [profile, setProfile] = useState(workspace.companyProfile);
  const [webhook, setWebhook] = useState("");
  const [removeWebhook, setRemoveWebhook] = useState(false);
  const [emails, setEmails] = useState(workspace.notifyEmails.join(", "));

  const dirty =
    name !== workspace.name ||
    website !== (workspace.website ?? "") ||
    profile !== workspace.companyProfile ||
    emails !== workspace.notifyEmails.join(", ") ||
    webhook.trim() !== "" ||
    removeWebhook;

  /** Loads a saved workspace into the form, so the server's normalized values count as clean. */
  const reset = (saved: Workspace) => {
    setName(saved.name);
    setWebsite(saved.website ?? "");
    setProfile(saved.companyProfile);
    setWebhook("");
    setRemoveWebhook(false);
    setEmails(saved.notifyEmails.join(", "));
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const body: WorkspaceUpdate = {
      name,
      website: website.trim() || null,
      companyProfile: profile,
      notifyEmails: emails.split(",").map((s) => s.trim()).filter(Boolean),
    };
    // The saved webhook is never loaded into the form, so only send it when it changes.
    if (webhook.trim()) body.slackWebhookUrl = webhook.trim();
    else if (removeWebhook) body.slackWebhookUrl = null;
    update.mutate(body, {
      onSuccess: (saved) => {
        // Update the cache in the same render as the form, so `dirty` never sees stale values.
        queryClient.setQueryData(["workspace"], saved);
        reset(saved);
      },
    });
  };

  return (
    <form onSubmit={submit} className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <section className="card space-y-6 p-6 animate-rise">
        <Field label="Company name">
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </Field>
        <Field label="Website" hint="Competitor discovery starts from this site.">
          <UrlInput value={website} onChange={(e) => setWebsite(e.target.value)} placeholder="yourcompany.com" />
        </Field>
        <Field
          label="Company profile"
          hint="The agent reads this before every run to judge what matters to you: your product, plans and prices, who you sell to, where you win and where you're weak."
        >
          <Textarea rows={14} value={profile} onChange={(e) => setProfile(e.target.value)} />
        </Field>
      </section>

      <div className="space-y-6 self-start">
        <aside className="card space-y-6 p-6 animate-rise [animation-delay:100ms]">
          <h2 className="text-base font-semibold tracking-tight">Delivery</h2>
          <p className="text-sm text-fg-muted">Approved reports are sent here. Nothing is sent without your approval.</p>
          <Field
            label="Slack webhook URL"
            hint={
              workspace.slackConfigured &&
              !removeWebhook && (
                <>
                  A webhook is saved. Paste a new URL to replace it, or{" "}
                  <button type="button" className="underline underline-offset-2 hover:text-fg" onClick={() => setRemoveWebhook(true)}>
                    remove it
                  </button>
                  .
                </>
              )
            }
          >
            <Input
              type="url"
              value={webhook}
              onChange={(e) => setWebhook(e.target.value)}
              placeholder={workspace.slackConfigured && !removeWebhook ? "Saved webhook (hidden)" : "https://hooks.slack.com/…"}
            />
          </Field>
          <Field label="Email recipients" hint="Comma-separated">
            <Input value={emails} onChange={(e) => setEmails(e.target.value)} placeholder="founder@company.com" />
          </Field>
        </aside>
        <DeleteCompanyCard workspace={workspace} />
      </div>

      {dirty && canWrite && (
        <div className="card sticky bottom-4 z-10 flex flex-wrap items-center justify-between gap-3 px-5 py-3 shadow-lg animate-rise [animation-duration:150ms] lg:col-span-2">
          <p className="text-sm font-medium">You have unsaved changes</p>
          <div className="flex gap-2">
            <Button type="button" variant="ghost" onClick={() => reset(workspace)} disabled={update.isPending}>
              Discard
            </Button>
            <Button type="submit" disabled={update.isPending}>
              Save changes
            </Button>
          </div>
        </div>
      )}
    </form>
  );
}

export function SettingsPage() {
  const { data: workspace } = useWorkspace();
  return (
    <>
      <PageHeader eyebrow="Company" title="Settings" />
      {workspace && <SettingsForm workspace={workspace} />}
    </>
  );
}
