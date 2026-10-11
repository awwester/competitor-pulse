import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Field, Input, Textarea } from "@/components/ui/Field";
import { PageHeader } from "@/components/ui/PageHeader";
import { useCanWrite } from "@/hooks/useMeta";
import { useUpdateWorkspace, useWorkspace } from "@/hooks/useWorkspace";
import type { Workspace, WorkspaceUpdate } from "@/types/api";

function SettingsForm({ workspace }: { workspace: Workspace }) {
  const canWrite = useCanWrite();
  const update = useUpdateWorkspace();
  const [name, setName] = useState(workspace.name);
  const [website, setWebsite] = useState(workspace.website ?? "");
  const [profile, setProfile] = useState(workspace.companyProfile);
  const [webhook, setWebhook] = useState("");
  const [removeWebhook, setRemoveWebhook] = useState(false);
  const [emails, setEmails] = useState(workspace.notifyEmails.join(", "));

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
      onSuccess: () => {
        setWebhook("");
        setRemoveWebhook(false);
      },
    });
  };

  return (
    <form onSubmit={submit} className="grid gap-12 lg:grid-cols-[1fr_20rem]">
      <section className="card space-y-6 p-6 animate-rise">
        <Field label="Company name">
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </Field>
        <Field label="Website" hint="Competitor discovery starts from this site.">
          <Input type="url" value={website} onChange={(e) => setWebsite(e.target.value)} placeholder="https://yourcompany.com" />
        </Field>
        <Field
          label="Company profile"
          hint="The agent reads this before every run to judge what matters to you: your product, plans and prices, who you sell to, where you win and where you're weak."
        >
          <Textarea rows={14} value={profile} onChange={(e) => setProfile(e.target.value)} />
        </Field>
      </section>

      <aside className="card space-y-6 self-start p-6 animate-rise [animation-delay:100ms]">
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
        <Button type="submit" disabled={!canWrite || update.isPending} className="w-full">
          Save settings
        </Button>
      </aside>
    </form>
  );
}

export function SettingsPage() {
  const { data: workspace } = useWorkspace();
  return (
    <>
      <PageHeader eyebrow="Workspace" title="Settings" />
      {workspace && <SettingsForm workspace={workspace} />}
    </>
  );
}
