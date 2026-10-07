import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useDeletePage, useUpdatePage } from "@/hooks/useCompetitors";
import { cn } from "@/lib/format";
import type { TrackedPage } from "@/types/api";

export function PageRow({ page, canWrite }: { page: TrackedPage; canWrite: boolean }) {
  const updatePage = useUpdatePage();
  const deletePage = useDeletePage();

  return (
    <li className="flex items-center gap-3 px-3 py-2 text-sm">
      <span className="w-20 shrink-0 text-xs font-medium capitalize text-fg-muted">
        {page.pageType}
      </span>
      <div className="min-w-0 flex-1">
        <a
          href={page.url}
          target="_blank"
          rel="noreferrer"
          className={cn("block truncate font-mono text-xs hover:text-accent", !page.isActive && "text-fg-faint line-through")}
        >
          {page.url}
        </a>
        {page.rationale && <p className="mt-0.5 text-xs text-fg-faint">{page.rationale}</p>}
      </div>
      {canWrite && (
        <>
          <label className="flex cursor-pointer items-center gap-1.5 text-xs text-fg-faint">
            <input
              type="checkbox"
              className="accent-accent"
              checked={page.isActive}
              onChange={(e) => updatePage.mutate({ id: page.id, isActive: e.target.checked })}
            />
            active
          </label>
          <Button
            variant="ghost"
            size="sm"
            aria-label="Stop tracking page"
            onClick={() => deletePage.mutate(page.id)}
          >
            <Trash2 className="size-3.5" />
          </Button>
        </>
      )}
    </li>
  );
}
