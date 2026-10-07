import { NavLink, Outlet } from "react-router";

import { PulseMark } from "@/components/layout/PulseMark";
import { useMeta } from "@/hooks/useMeta";
import { cn } from "@/lib/format";

const NAV = [
  { to: "/", label: "Brief", end: true },
  { to: "/runs", label: "Runs" },
  { to: "/competitors", label: "Competitors" },
  { to: "/settings", label: "Settings" },
];

export function AppShell() {
  const { data: meta } = useMeta();

  return (
    <div className="min-h-screen">
      {meta?.demoMode && (
        <div className="bg-accent px-4 py-2 text-center text-xs text-white">
          Read-only demo: browse real agent runs.{" "}
          <a
            className="font-medium underline underline-offset-4"
            href="https://github.com/awwester/competitor-pulse"
          >
            Self-host it
          </a>{" "}
          to track your own competitors.
        </div>
      )}

      <header className="sticky top-0 z-10 border-b border-line bg-surface/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 sm:px-6">
          <NavLink to="/" className="group flex items-center gap-2">
            <span className="grid size-8 place-items-center rounded-lg bg-accent text-white">
              <PulseMark className="h-4 w-6 transition-transform group-hover:scale-x-110" />
            </span>
            <span className="hidden text-base font-semibold tracking-tight sm:inline">Competitor Pulse</span>
          </NavLink>

          <nav className="flex gap-1 overflow-x-auto">
            {NAV.map(({ to, label, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                    isActive ? "bg-subtle text-fg" : "text-fg-muted hover:text-fg",
                  )
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>

          {meta && (
            <span className="ml-auto hidden items-center gap-2 rounded-full border border-line px-3 py-1 font-mono text-[11px] text-fg-muted md:inline-flex">
              <span className="size-1.5 rounded-full bg-ok" />
              {meta.agentModel} · {meta.scheduleCron}
            </span>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <Outlet />
      </main>

      <footer className="mx-auto max-w-6xl px-4 pb-10 sm:px-6">
        <p className="border-t border-line pt-4 text-xs text-fg-faint">
          Competitor Pulse · open source · built with the Claude Agent SDK
        </p>
      </footer>
    </div>
  );
}
