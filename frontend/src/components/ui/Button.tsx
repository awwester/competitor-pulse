import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/format";

const VARIANTS = {
  primary: "bg-accent text-white shadow-sm hover:bg-accent/90",
  outline: "border border-line bg-surface text-fg shadow-sm hover:bg-subtle",
  ghost: "text-fg-muted hover:text-fg hover:bg-subtle",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof VARIANTS;
  size?: "sm" | "md";
}

export function Button({ variant = "primary", size = "md", className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors",
        "disabled:pointer-events-none disabled:opacity-40 cursor-pointer",
        size === "sm" ? "h-8 px-3 text-xs" : "h-10 px-4 text-sm",
        VARIANTS[variant],
        className,
      )}
      {...props}
    />
  );
}
