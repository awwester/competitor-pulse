import { Link, useNavigate } from "react-router";

import { DiscoveryForm } from "@/components/discovery/DiscoveryForm";
import { RunStatusBadge } from "@/components/runs/RunStatusBadge";
import { usePendingCompanyDiscovery, useStartDiscovery } from "@/hooks/useDiscovery";
import { useWorkspace } from "@/hooks/useWorkspace";
import type { RunSummary } from "@/types/api";

function DiscoveryStatus({ run }: { run: RunSummary }) {
  const reviewing = run.status === "awaiting_review";

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
      <RunStatusBadge status={run.status} />
      <span className="text-fg-muted">
        {reviewing ? "Nothing is tracked until you approve the shortlist." : "The agent is reading your site."}
      </span>
      <Link to={`/runs/${run.id}`} className="font-medium text-accent hover:underline underline-offset-4">
        {reviewing ? "Review competitors →" : "Watch it run →"}
      </Link>
    </div>
  );
}

/**
 * First-run setup: the company website is the only thing the user has to type, and it's
 * pre-filled when already saved in Settings. Once discovery starts, the card follows it instead.
 * `manualLink` points to the competitors page, so it's hidden there.
 */
export function OnboardingCard({ manualLink = true }: { manualLink?: boolean }) {
  const { data: workspace } = useWorkspace();
  const discovery = usePendingCompanyDiscovery();
  const start = useStartDiscovery();
  const navigate = useNavigate();

  const title = discovery
    ? discovery.status === "awaiting_review"
      ? "Your competitor shortlist is ready"
      : "Finding your competitors…"
    : workspace?.website
      ? "Find your competitors"
      : "Start with your website";

  return (
    <section className="card p-6 animate-rise sm:p-8">
      <p className="eyebrow mb-3">Get started</p>
      <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-2 mb-6 max-w-prose text-sm text-fg-muted">
        The agent reads your site, fills in your company name and profile, and suggests the
        competitors worth watching. You approve the list, then it finds each competitor's pricing,
        changelog and careers pages.
      </p>
      {discovery ? (
        <DiscoveryStatus run={discovery} />
      ) : (
        workspace && (
          <DiscoveryForm
            initial={workspace.website}
            pending={start.isPending}
            onSubmit={(website) => start.mutate(website, { onSuccess: (run) => navigate(`/runs/${run.id}`) })}
          />
        )
      )}
      {manualLink && !discovery && (
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
