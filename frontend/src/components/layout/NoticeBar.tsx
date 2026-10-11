import type { ReactNode } from "react";

import { cn } from "@/lib/format";

const TONES = {
  accent: "bg-accent text-white",
  wait: "border-b border-wait/30 bg-wait-soft text-wait",
};

/** Full-width strip above the header for app-wide notices. */
export function NoticeBar({ tone, children }: { tone: keyof typeof TONES; children: ReactNode }) {
  return <div className={cn("px-4 py-2 text-center text-xs", TONES[tone])}>{children}</div>;
}
