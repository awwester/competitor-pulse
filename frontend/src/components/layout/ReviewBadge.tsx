import { useDashboard } from "@/hooks/useDashboard";

/** Count of runs waiting at the approval gate; renders nothing when there are none. */
export function ReviewBadge() {
  const count = useDashboard().data?.pendingReviews.length ?? 0;
  if (!count) return null;

  return (
    <span
      aria-label={`${count} awaiting review`}
      className="ml-1.5 inline-grid min-w-4.5 place-items-center rounded-full bg-wait px-1 text-[10px] font-semibold leading-4.5 text-white"
    >
      {count}
    </span>
  );
}
