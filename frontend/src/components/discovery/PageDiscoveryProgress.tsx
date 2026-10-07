import { useActivePageDiscoveries } from "@/hooks/useDiscovery";

/** Shown while the agent is still finding pages for newly approved competitors. */
export function PageDiscoveryProgress() {
  const active = useActivePageDiscoveries();
  if (!active.size) return null;

  return (
    <div className="flex items-start gap-4 rounded-xl border border-accent/20 bg-accent-soft px-5 py-4 animate-rise">
      <span className="mt-1.5 size-2 shrink-0 rounded-full bg-accent animate-pulse" />
      <div>
        <p className="eyebrow text-accent">Setting up</p>
        <p className="mt-1 text-sm text-fg-muted">
          Finding the pages worth watching for{" "}
          <strong className="text-fg">
            {active.size} competitor{active.size === 1 ? "" : "s"}
          </strong>
          , one at a time. Pages appear as they're found. A first check then captures a baseline of
          every page, so changes show up as findings from the next check on.
        </p>
      </div>
    </div>
  );
}
