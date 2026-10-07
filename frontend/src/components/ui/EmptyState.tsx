import type { ReactNode } from "react";

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-line bg-surface/50 px-6 py-14 text-center">
      <p className="text-base font-semibold text-fg">{title}</p>
      {children && <div className="mx-auto mt-3 max-w-md text-sm text-fg-muted">{children}</div>}
    </div>
  );
}
