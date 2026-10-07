import { ArrowUpRight } from "lucide-react";

import { cn } from "@/lib/format";
import type { CompetitorSuggestion } from "@/types/api";

interface SuggestionRowProps {
  suggestion: CompetitorSuggestion;
  /** When provided, the row can be ticked in or out (while the discovery awaits review). */
  onToggle?: (suggestion: CompetitorSuggestion) => void;
}

export function SuggestionRow({ suggestion, onToggle }: SuggestionRowProps) {
  return (
    <li className={cn("flex gap-4 px-5 py-4", !suggestion.isSelected && "opacity-45")}>
      <input
        type="checkbox"
        aria-label={`Track ${suggestion.name}`}
        className="mt-1 size-4 shrink-0 accent-accent"
        checked={suggestion.isSelected}
        disabled={!onToggle}
        onChange={() => onToggle?.(suggestion)}
      />
      <div className="min-w-0">
        <div className="flex flex-wrap items-baseline gap-x-3">
          <h3 className={cn("font-semibold tracking-tight", !suggestion.isSelected && "line-through")}>
            {suggestion.name}
          </h3>
          <a
            href={suggestion.website}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 truncate text-xs text-fg-faint hover:text-accent"
          >
            {suggestion.website} <ArrowUpRight className="size-3" />
          </a>
        </div>
        <p className="mt-1 max-w-prose text-sm text-fg-muted">{suggestion.rationale || "Added by you"}</p>
      </div>
    </li>
  );
}
