import { NavLink, Outlet } from "react-router";

import { MainNav } from "@/components/layout/MainNav";
import { MobileMenu } from "@/components/layout/MobileMenu";
import { NextCheck } from "@/components/layout/NextCheck";
import { PulseMark } from "@/components/layout/PulseMark";
import { WorkspaceSwitcher } from "@/components/workspace/WorkspaceSwitcher";
import { useMeta } from "@/hooks/useMeta";

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
            See the code
          </a>{" "}
          or run it locally to track your own competitors.
        </div>
      )}

      <header className="sticky top-0 z-10 border-b border-line bg-surface/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 sm:px-6">
          <NavLink to="/" className="group flex items-center gap-2">
            <span className="grid size-8 place-items-center rounded-lg bg-accent text-white">
              <PulseMark className="h-4 w-6 transition-transform group-hover:scale-x-110" />
            </span>
            <span className="hidden text-base font-semibold tracking-tight lg:inline">Competitor Pulse</span>
          </NavLink>

          <WorkspaceSwitcher />

          <MainNav />
          <NextCheck className="ml-auto hidden shrink-0 rounded-full border border-line px-3 py-1 lg:inline-flex" />
          <MobileMenu />
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <Outlet />
      </main>

      <footer className="mx-auto max-w-6xl px-4 pb-10 sm:px-6">
        <p className="border-t border-line pt-4 text-xs text-fg-faint">
          Competitor Pulse · open source · built with the Claude Agent SDK
          {meta && <> · {meta.agentModel}</>}
        </p>
      </footer>
    </div>
  );
}
