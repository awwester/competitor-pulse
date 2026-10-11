import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";

import { useCanWrite } from "@/hooks/useMeta";
import { useCurrentWorkspace, useWorkspaces } from "@/hooks/useWorkspace";
import { cn } from "@/lib/format";

const ITEM = "flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition-colors hover:bg-subtle";

/** Header menu that switches the company everything else is scoped to. */
export function WorkspaceSwitcher() {
  const { workspaceId, switchTo } = useCurrentWorkspace();
  const { data: workspaces = [] } = useWorkspaces();
  const canWrite = useCanWrite();
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const current = workspaces.find((w) => w.id === workspaceId);

  useEffect(() => {
    if (!open) return;
    const onPointer = (e: PointerEvent) => {
      if (!root.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const select = (id: string) => {
    setOpen(false);
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
        <div role="menu" className="card absolute top-full left-0 z-20 mt-2 w-64 p-1 animate-rise [animation-duration:150ms]">
          <p className="eyebrow px-2.5 pt-1.5 pb-1">Companies</p>
          {workspaces.map((w) => (
            <button key={w.id} type="button" role="menuitem" onClick={() => select(w.id)} className={ITEM}>
              <span className={cn("min-w-0 flex-1 truncate", w.id === workspaceId && "font-medium")}>{w.name}</span>
              {w.id === workspaceId && <Check className="size-4 shrink-0 text-accent" />}
            </button>
          ))}
          {canWrite && (
            <>
              <div className="my-1 border-t border-line" />
              <Link to="/companies/new" role="menuitem" onClick={() => setOpen(false)} className={cn(ITEM, "text-fg-muted hover:text-fg")}>
                <Plus className="size-4" /> Add company
              </Link>
            </>
          )}
        </div>
      )}
    </div>
  );
}
