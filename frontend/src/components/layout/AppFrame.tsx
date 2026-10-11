import type { ReactNode } from "react";
import { NavLink } from "react-router";

import { NoticeBar } from "@/components/layout/NoticeBar";
import { PulseMark } from "@/components/layout/PulseMark";
import { useMeta } from "@/hooks/useMeta";

/** Notices, header and footer around every screen; `header` holds the controls beside the logo. */
export function AppFrame({ header, children }: { header?: ReactNode; children: ReactNode }) {
  const { data: meta } = useMeta();

  return (
    <div className="min-h-screen">
      {meta?.demoMode && (
        <NoticeBar tone="accent">
          Read-only demo: browse real agent runs.{" "}
          <a
            className="font-medium underline underline-offset-4"
            href="https://github.com/awwester/competitor-pulse"
          >
            See the code
          </a>{" "}
          or run it locally to track your own competitors.
        </NoticeBar>
      )}
      {meta && !meta.demoMode && !meta.agentConfigured && (
        <NoticeBar tone="wait">
          The agent needs an API key: add <code className="font-mono">ANTHROPIC_API_KEY</code> to{" "}
          <code className="font-mono">.env</code>, then restart with{" "}
          <code className="font-mono">make dev</code>.
        </NoticeBar>
      )}

      <header className="sticky top-0 z-10 border-b border-line bg-surface/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 sm:px-6">
          <NavLink to="/" className="group flex items-center gap-2">
            <span className="grid size-8 place-items-center rounded-lg bg-accent text-white">
              <PulseMark className="h-4 w-6 transition-transform group-hover:scale-x-110" />
            </span>
            <span className="hidden text-base font-semibold tracking-tight lg:inline">Competitor Pulse</span>
          </NavLink>

          {header}
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        {children}
      </main>

      <footer className="mx-auto max-w-6xl px-4 pb-10 sm:px-6">
        <p className="border-t border-line pt-4 text-xs text-fg-faint">
          Competitor Pulse · open source · built with the Claude Agent SDK
          {meta && <> · {meta.analystModel}</>}
        </p>
      </footer>
    </div>
  );
}
