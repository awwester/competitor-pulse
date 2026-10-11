import { cn } from "@/lib/format";

interface SegmentedControlProps<T extends string> {
  options: { value: T; label: string; count?: number }[];
  value: T;
  onChange: (value: T) => void;
  label: string;
}

export function SegmentedControl<T extends string>({ options, value, onChange, label }: SegmentedControlProps<T>) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-lg border border-line bg-surface p-0.5 shadow-sm">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          role="radio"
          aria-checked={option.value === value}
          onClick={() => onChange(option.value)}
          className={cn(
            "inline-flex h-8 cursor-pointer items-center gap-1.5 rounded-md px-3 text-sm font-medium transition-colors",
            option.value === value ? "bg-subtle text-fg" : "text-fg-muted hover:text-fg",
          )}
        >
          {option.label}
          {option.count !== undefined && <span className="text-xs tabular-nums text-fg-faint">{option.count}</span>}
        </button>
      ))}
    </div>
  );
}
