import { useDashboard } from "@/hooks/useDashboard";
import { useMeta } from "@/hooks/useMeta";
import { cn, formatWeekdayTime } from "@/lib/format";

export function NextCheck({ className }: { className?: string }) {
  const { data: meta } = useMeta();
  // Scheduled checks skip a company with no tracked pages.
  const hasPages = !!useDashboard().data?.pageCount;
  if (!meta?.nextCheckAt || !hasPages) return null;

  return (
    <span className={cn("flex items-center gap-2 whitespace-nowrap text-xs text-fg-muted", className)}>
      <span className="size-1.5 rounded-full bg-ok" />
      Next check {formatWeekdayTime(meta.nextCheckAt)}
    </span>
  );
}
