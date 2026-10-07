import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/format";

const control =
  "w-full rounded-sm border border-rule bg-white/60 px-3 py-2 text-sm text-ink placeholder:text-ink-faint " +
  "focus:border-ink focus:bg-white focus:outline-none transition-colors";

export function Field({ label, hint, children }: { label: string; hint?: ReactNode; children: ReactNode }) {
  return (
    <label className="block space-y-1.5">
      <span className="eyebrow">{label}</span>
      {children}
      {hint && <span className="block text-xs text-ink-faint">{hint}</span>}
    </label>
  );
}

export const Input = ({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) => (
  <input className={cn(control, "h-10", className)} {...props} />
);

export const Textarea = ({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) => (
  <textarea className={cn(control, "leading-relaxed", className)} {...props} />
);

export const Select = ({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) => (
  <select className={cn(control, "h-10 capitalize", className)} {...props} />
);
