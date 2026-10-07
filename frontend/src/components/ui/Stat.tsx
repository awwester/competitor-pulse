import { cn } from "@/lib/format";

export function Stat({ label, value, className }: { label: string; value: string | number; className?: string }) {
  return (
    <div className={cn("border-l border-rule pl-4", className)}>
      <p className="eyebrow">{label}</p>
      <p className="mt-1 font-mono text-2xl tabular-nums">{value}</p>
    </div>
  );
}
