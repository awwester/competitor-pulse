import type { ReactNode } from "react";

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="border border-dashed border-rule px-6 py-14 text-center">
      <p className="font-display text-2xl italic text-ink-soft">{title}</p>
      {children && <div className="mx-auto mt-3 max-w-md text-sm text-ink-faint">{children}</div>}
    </div>
  );
}
