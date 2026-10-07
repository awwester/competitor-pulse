export function Stat({ label, value, className }: { label: string; value: string | number; className?: string }) {
  return (
    <div className={className}>
      <p className="eyebrow">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight tabular-nums">{value}</p>
    </div>
  );
}
