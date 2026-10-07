import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useDeletePage, useUpdatePage } from "@/hooks/useCompetitors";
import { cn } from "@/lib/format";
import type { TrackedPage } from "@/types/api";

export function PageRow({ page, canWrite }: { page: TrackedPage; canWrite: boolean }) {
  const updatePage = useUpdatePage();
  const deletePage = useDeletePage();

  return (
    <li className="flex items-center gap-3 border-t border-rule/70 py-2.5 text-sm">
      <span className="w-20 shrink-0 font-mono text-[11px] uppercase tracking-wider text-ink-faint">
        {page.pageType}
      </span>
      <a
        href={page.url}
        target="_blank"
        rel="noreferrer"
        className={cn("min-w-0 flex-1 truncate font-mono text-xs hover:underline", !page.isActive && "text-ink-faint line-through")}
      >
        {page.url}
      </a>
      {canWrite && (
        <>
          <label className="flex cursor-pointer items-center gap-1.5 font-mono text-[11px] text-ink-faint">
            <input
              type="checkbox"
              className="accent-ink"
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
