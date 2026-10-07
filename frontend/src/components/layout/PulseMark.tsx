import { cn } from "@/lib/format";

/** The pulse line used in the logo; the line travels while `live`. */
export function PulseMark({ live = false, className }: { live?: boolean; className?: string }) {
  return (
    <svg viewBox="0 0 64 24" className={cn("h-6 w-16", className)} aria-hidden>
      <path
        d="M0 13h16l5-10 8 18 6-12 4 4h25"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={live ? "animate-trace [stroke-dasharray:80]" : undefined}
      />
    </svg>
  );
}
