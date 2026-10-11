import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children?: ReactNode;
}) {
  return (
    <header className="mb-8 flex flex-wrap items-end justify-between gap-4 animate-rise">
      <div>
        <p className="eyebrow mb-1">{eyebrow}</p>
        <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      </div>
      {children && (
        // Below `sm` the actions span the width, so stacked buttons line up.
        <div className="flex w-full flex-wrap items-center gap-2 *:flex-1 sm:w-auto sm:*:flex-none">{children}</div>
      )}
    </header>
  );
}
