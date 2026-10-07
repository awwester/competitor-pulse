import { Link } from "react-router";

import { PageRow } from "@/components/competitors/PageRow";
import { useCompetitors } from "@/hooks/useCompetitors";
import { useCanWrite } from "@/hooks/useMeta";
import type { RunDetail } from "@/types/api";

export function PageDiscoveryView({ run, live }: { run: RunDetail; live: boolean }) {
  const canWrite = useCanWrite();
  const { data: competitors } = useCompetitors(live);
  const competitor = competitors?.find((c) => c.id === run.competitorId);
  if (!competitor) return null;

  return (
    <section>
      <div className="mb-4 flex items-baseline justify-between">
        <h2 className="text-lg font-semibold tracking-tight">Pages tracked for {competitor.name}</h2>
        <Link to="/competitors" className="text-xs font-medium text-accent hover:underline underline-offset-4">
          All competitors →
        </Link>
      </div>
      <ul className="card divide-y divide-line">
        {competitor.pages.map((page) => (
          <PageRow key={page.id} page={page} canWrite={canWrite} />
        ))}
        {competitor.pages.length === 0 && (
          <li className="px-3 py-3 text-sm text-fg-faint">{live ? "Looking…" : "No pages tracked yet."}</li>
        )}
      </ul>
    </section>
  );
}
