import { cn } from "@/lib/format";

/** Five ascending bars, filled up to the finding's significance. */
export function SignificanceMeter({ value, className }: { value: number; className?: string }) {
  return (
    <div
      className={cn("flex items-end gap-[3px]", className)}
      role="img"
      aria-label={`Significance ${value} of 5`}
      title={`Significance ${value}/5`}
    >
      {[1, 2, 3, 4, 5].map((level) => (
        <span
          key={level}
          className={cn(
            "w-[5px] rounded-[1px]",
            level <= value ? (value >= 4 ? "bg-signal" : "bg-ink") : "bg-rule",
          )}
          style={{ height: 6 + level * 4 }}
        />
      ))}
    </div>
  );
}
