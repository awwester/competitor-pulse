import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/format";

const VARIANTS = {
  primary: "bg-ink text-paper hover:bg-ink/85",
  signal: "bg-signal text-white hover:bg-signal/90",
  outline: "border border-ink/25 text-ink hover:border-ink hover:bg-ink/5",
  ghost: "text-ink-soft hover:text-ink hover:bg-ink/5",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof VARIANTS;
  size?: "sm" | "md";
}

export function Button({ variant = "primary", size = "md", className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-sm font-medium transition-colors",
        "disabled:pointer-events-none disabled:opacity-40 cursor-pointer",
        size === "sm" ? "h-8 px-3 text-xs" : "h-10 px-4 text-sm",
        VARIANTS[variant],
        className,
      )}
      {...props}
    />
  );
}
