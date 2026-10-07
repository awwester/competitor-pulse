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
    <header className="mb-10 flex flex-wrap items-end justify-between gap-4 border-b border-ink pb-5 animate-rise">
      <div>
        <p className="eyebrow mb-2">{eyebrow}</p>
        <h1 className="font-display text-4xl leading-none sm:text-5xl">{title}</h1>
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </header>
  );
}
