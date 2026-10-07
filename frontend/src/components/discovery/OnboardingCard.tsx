import { Sparkles } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Field";
import { useStartDiscovery } from "@/hooks/useDiscovery";
import { useCanWrite } from "@/hooks/useMeta";
import { useWorkspace } from "@/hooks/useWorkspace";

function DiscoveryForm({ savedWebsite }: { savedWebsite: string | null }) {
  const canWrite = useCanWrite();
  const navigate = useNavigate();
  const start = useStartDiscovery();
  const [website, setWebsite] = useState(savedWebsite ?? "");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    start.mutate(website, { onSuccess: (run) => navigate(`/runs/${run.id}`) });
  };

  return (
    <form onSubmit={submit} className="mt-6 flex flex-wrap gap-2">
      <Input
        required
        type="url"
        value={website}
        onChange={(e) => setWebsite(e.target.value)}
        placeholder="https://yourcompany.com"
        className="min-w-0 flex-1 basis-72"
      />
      <Button type="submit" disabled={!canWrite || start.isPending}>
        <Sparkles className="size-4" /> Discover competitors
      </Button>
    </form>
  );
}

/**
 * First-run setup: the company website is the only thing the user has to type, and it's
 * pre-filled when already saved in Settings. `manualLink` points to the competitors page, so
 * it's hidden there.
 */
export function OnboardingCard({ manualLink = true }: { manualLink?: boolean }) {
  const { data: workspace } = useWorkspace();

  return (
    <section className="card p-6 animate-rise sm:p-8">
      <p className="eyebrow mb-3">Get started</p>
      <h2 className="text-2xl font-semibold tracking-tight">
        {workspace?.website ? "Find your competitors" : "Start with your website"}
      </h2>
      <p className="mt-2 max-w-prose text-sm text-fg-muted">
        The agent reads your site, writes a company profile and suggests the competitors worth
        watching. You approve the list, then it finds each competitor's pricing, changelog and
        careers pages.
      </p>
      {workspace && <DiscoveryForm savedWebsite={workspace.website} />}
      {manualLink && (
        <p className="mt-4 text-xs text-fg-faint">
          Prefer to set it up by hand?{" "}
          <Link to="/competitors" className="underline underline-offset-4 hover:text-fg">
            Add competitors yourself
          </Link>
          .
        </p>
      )}
    </section>
  );
}
