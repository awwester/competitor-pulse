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

const today = new Date().toLocaleDateString("en", {
  weekday: "long",
  month: "long",
  day: "numeric",
  year: "numeric",
});

export function AppShell() {
  const { data: meta } = useMeta();

  return (
    <div className="min-h-screen">
      {meta?.demoMode && (
        <div className="bg-ink px-4 py-2 text-center font-mono text-xs text-paper">
          Read-only demo: browse real agent runs.{" "}
          <a
            className="underline decoration-signal underline-offset-4"
            href="https://github.com/awwester/competitor-pulse"
          >
            Self-host it
          </a>{" "}
          to track your own competitors.
        </div>
      )}

      <header className="mx-auto max-w-6xl px-4 pt-8 sm:px-6">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-rule pb-2 font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
          <span>{today}</span>
          {meta && (
            <span>
              Agent · {meta.agentModel} · schedule <span className="text-ink-soft">{meta.scheduleCron}</span>
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-end justify-between gap-6 py-5">
          <NavLink to="/" className="group flex items-center gap-3">
            <PulseMark className="text-signal transition-transform group-hover:scale-x-110" />
            <span className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              Competitor Pulse
            </span>
          </NavLink>

          <nav className="flex gap-1">
            {NAV.map(({ to, label, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    "px-3 py-1.5 font-mono text-xs uppercase tracking-[0.12em] transition-colors",
                    isActive ? "bg-ink text-paper" : "text-ink-soft hover:text-ink",
                  )
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="h-[3px] border-y border-ink" />
      </header>

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <Outlet />
      </main>

      <footer className="mx-auto max-w-6xl px-4 pb-10 sm:px-6">
        <p className="border-t border-rule pt-4 font-mono text-[11px] text-ink-faint">
          Competitor Pulse · open source · built with the Claude Agent SDK
        </p>
      </footer>
    </div>
  );
}
