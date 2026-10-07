import { ArrowUpRight, CornerDownRight, EyeOff, Undo2 } from "lucide-react";
import { Link } from "react-router";

import { SignificanceMeter } from "@/components/runs/SignificanceMeter";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/format";
import type { Finding } from "@/types/api";

interface FindingCardProps {
  finding: Finding;
  /** When provided, shows a dismiss/restore control (used while a run awaits review). */
  onToggleDismissed?: (finding: Finding) => void;
  showRunLink?: boolean;
  index?: number;
}

export function FindingCard({ finding, onToggleDismissed, showRunLink, index = 0 }: FindingCardProps) {
  return (
    <article
      className={cn(
        "grid grid-cols-[auto_1fr] gap-x-4 px-4 py-6 animate-rise sm:gap-x-5 sm:px-6",
        finding.isDismissed && "opacity-45",
      )}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <SignificanceMeter value={finding.significance} className="self-start pt-1" />

      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="rounded-md bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent capitalize">{finding.category}</span>
          <span className="eyebrow">{finding.competitorName}</span>
          <div className="ml-auto flex items-center gap-1">
            {finding.sourceUrl && (
              <a
                href={finding.sourceUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs text-fg-faint hover:text-accent"
              >
                source <ArrowUpRight className="size-3" />
              </a>
            )}
            {onToggleDismissed && (
              <Button variant="ghost" size="sm" onClick={() => onToggleDismissed(finding)}>
                {finding.isDismissed ? <Undo2 className="size-3.5" /> : <EyeOff className="size-3.5" />}
                {finding.isDismissed ? "Restore" : "Dismiss"}
              </Button>
            )}
          </div>
        </div>

        <h3 className={cn("mt-2 text-lg font-semibold leading-snug tracking-tight", finding.isDismissed && "line-through")}>
          {finding.title}
        </h3>
        <p className="mt-2 max-w-prose text-[15px] leading-relaxed text-fg-muted">{finding.summary}</p>

        {finding.evidence && (
          <blockquote className="mt-4 max-w-prose rounded-md border-l-2 border-accent bg-subtle px-4 py-2 font-mono text-xs leading-relaxed text-fg-muted">
            {finding.evidence}
          </blockquote>
        )}

        {finding.recommendedAction && (
          <p className="mt-4 flex max-w-prose gap-2 text-sm font-medium">
            <CornerDownRight className="mt-0.5 size-4 shrink-0 text-accent" />
            {finding.recommendedAction}
          </p>
        )}

        {showRunLink && (
          <Link
            to={`/runs/${finding.runId}`}
            className="mt-4 inline-block text-xs font-medium text-accent hover:underline underline-offset-4"
          >
            View run →
          </Link>
        )}
      </div>
    </article>
  );
}
