import { useMeta } from "@/hooks/useMeta";
import { cn, formatWeekdayTime } from "@/lib/format";

export function NextCheck({ className }: { className?: string }) {
  const { data: meta } = useMeta();
  if (!meta?.nextCheckAt) return null;

  return (
    <span className={cn("flex items-center gap-2 whitespace-nowrap text-xs text-fg-muted", className)}>
      <span className="size-1.5 rounded-full bg-ok" />
      Next check {formatWeekdayTime(meta.nextCheckAt)}
    </span>
  );
}
