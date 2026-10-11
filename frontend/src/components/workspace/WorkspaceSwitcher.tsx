import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { Link } from "react-router";

import { MENU_ITEM, MENU_PANEL } from "@/components/ui/menu";
import { useDismiss } from "@/hooks/useDismiss";
import { useCanWrite } from "@/hooks/useMeta";
import { useCurrentWorkspace, useWorkspaces } from "@/hooks/useWorkspace";
import { cn } from "@/lib/format";

/** Header menu that switches the company everything else is scoped to. */
export function WorkspaceSwitcher() {
  const { workspaceId, switchTo } = useCurrentWorkspace();
  const { data: workspaces = [] } = useWorkspaces();
  const canWrite = useCanWrite();
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const current = workspaces.find((w) => w.id === workspaceId);

  const close = useCallback(() => setOpen(false), []);
  useDismiss(root, open, close);

  const select = (id: string) => {
    close();
    switchTo(id);
  };

  return (
    <div ref={root} className="relative">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="inline-flex h-8 max-w-48 cursor-pointer items-center gap-1.5 rounded-md border border-line bg-surface pr-2 pl-3 text-sm font-medium shadow-sm transition-colors hover:bg-subtle"
      >
        <span className="truncate">{current?.name}</span>
        <ChevronsUpDown className="size-3.5 shrink-0 text-fg-faint" />
      </button>

      {open && (
        <div role="menu" className={cn(MENU_PANEL, "left-0")}>
          <p className="eyebrow px-2.5 pt-1.5 pb-1">Companies</p>
          {workspaces.map((w) => (
            <button key={w.id} type="button" role="menuitem" onClick={() => select(w.id)} className={MENU_ITEM}>
              <span className={cn("min-w-0 flex-1 truncate", w.id === workspaceId && "font-medium")}>{w.name}</span>
              {w.id === workspaceId && <Check className="size-4 shrink-0 text-accent" />}
            </button>
          ))}
          {canWrite && (
            <>
              <div className="my-1 border-t border-line" />
              <Link to="/companies/new" role="menuitem" onClick={close} className={cn(MENU_ITEM, "text-fg-muted hover:text-fg")}>
                <Plus className="size-4" /> Add company
              </Link>
            </>
          )}
        </div>
      )}
    </div>
  );
}
