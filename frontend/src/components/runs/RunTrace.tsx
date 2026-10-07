import { useEffect, useRef, type ReactNode } from "react";

import { PulseMark } from "@/components/layout/PulseMark";
import { cn, formatUsd } from "@/lib/format";
import type { RunEvent } from "@/types/api";

const str = (value: unknown) => (typeof value === "string" ? value : "");

function elapsed(event: RunEvent, start: number): string {
  const seconds = Math.max(0, Math.round((new Date(event.createdAt).getTime() - start) / 1000));
  return `+${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}

function compactArgs(input: unknown): string {
  if (!input || typeof input !== "object") return "";
  return Object.entries(input as Record<string, unknown>)
    .map(([key, value]) => {
      const text = typeof value === "string" ? value : JSON.stringify(value);
      return `${key}: ${text.length > 40 ? `${text.slice(0, 40)}…` : text}`;
    })
    .join(", ");
}

function Collapsible({ summary, children, className }: { summary: ReactNode; children: ReactNode; className?: string }) {
  return (
    <details className={cn("group", className)}>
      <summary className="cursor-pointer list-none select-none hover:text-wire-text [&::-webkit-details-marker]:hidden">
        <span className="mr-1 inline-block transition-transform group-open:rotate-90">▸</span>
        {summary}
      </summary>
      <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap break-words border-l border-wire-line pl-3 text-[11px] leading-relaxed text-wire-dim">
        {children}
      </pre>
    </details>
  );
}

function EventBody({ event }: { event: RunEvent }) {
  const { payload } = event;
  switch (event.kind) {
    case "phase":
      return (
        <div className="pt-3">
          <span className="font-medium uppercase tracking-[0.14em] text-wire-text">■ {str(payload.title)}</span>
          {str(payload.detail) && <span className="text-wire-dim"> | {str(payload.detail)}</span>}
        </div>
      );
    case "thinking":
      return (
        <Collapsible summary={<span className="italic">thinking</span>} className="text-wire-dim">
          {str(payload.text)}
        </Collapsible>
      );
    case "text":
      return <p className="whitespace-pre-wrap text-wire-text">{str(payload.text)}</p>;
    case "tool_call":
      return (
        <p className="break-words">
          <span className="text-wire-call">→ {str(payload.name)}</span>
          <span className="text-wire-dim">({compactArgs(payload.input)})</span>
        </p>
      );
    case "tool_result": {
      const content = str(payload.content);
      return (
        <Collapsible
          className={payload.isError ? "text-danger" : "text-wire-dim"}
          summary={`← ${payload.isError ? "error" : "ok"} · ${content.length.toLocaleString()} chars`}
        >
          {content}
        </Collapsible>
      );
    }
    case "error":
      return <p className="text-danger">✕ {str(payload.message)}</p>;
    case "result":
      return (
        <p className="text-wire-ok">
          ✓ agent finished · {String(payload.numTurns)} turns · {formatUsd(Number(payload.costUsd ?? 0))}
        </p>
      );
  }
}

export function RunTrace({ events, live }: { events: RunEvent[]; live: boolean }) {
  const scroller = useRef<HTMLDivElement>(null);
  const start = events.length ? new Date(events[0].createdAt).getTime() : 0;

  useEffect(() => {
    if (live) scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [events.length, live]);

  return (
    <section className="overflow-hidden rounded-xl bg-wire text-wire-text shadow-lg">
      <header className="flex items-center justify-between border-b border-wire-line px-4 py-3">
        <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-wire-dim">Agent trace</span>
        <span className="flex items-center gap-2 font-mono text-[11px] text-wire-dim">
          {live ? "live" : `${events.length} events`}
          <PulseMark live={live} className={cn("h-4 w-10", live ? "text-wire-call" : "text-wire-line")} />
        </span>
      </header>

      <div ref={scroller} className="max-h-[70vh] overflow-y-auto px-4 py-3 font-mono text-xs leading-relaxed">
        {events.length === 0 && <p className="py-6 text-wire-dim">Waiting for the worker to pick up this run…</p>}
        <ol className="space-y-1.5">
          {events.map((event) => (
            <li key={event.id} className="grid grid-cols-[3.25rem_1fr] gap-2">
              <span className={cn("select-none text-wire-dim/60", event.kind === "phase" && "pt-3")}>
                {elapsed(event, start)}
              </span>
              <EventBody event={event} />
            </li>
          ))}
        </ol>
        {live && <span className="mt-2 ml-[3.75rem] inline-block h-3.5 w-2 bg-wire-text animate-blink" />}
      </div>
    </section>
  );
}
