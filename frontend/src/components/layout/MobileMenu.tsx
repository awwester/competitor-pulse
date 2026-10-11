import { Menu, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { NavLink } from "react-router";

import { NAV } from "@/components/layout/nav";
import { NextCheck } from "@/components/layout/NextCheck";
import { ReviewBadge } from "@/components/layout/ReviewBadge";
import { MENU_ITEM, MENU_PANEL } from "@/components/ui/menu";
import { useDashboard } from "@/hooks/useDashboard";
import { useDismiss } from "@/hooks/useDismiss";
import { cn } from "@/lib/format";

/** Header nav below `sm`: a menu button that opens the page links as a dropdown. */
export function MobileMenu() {
  const hasReviews = !!useDashboard().data?.pendingReviews.length;
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const close = useCallback(() => setOpen(false), []);
  useDismiss(root, open, close);

  return (
    <div ref={root} className="relative ml-auto sm:hidden">
      <button
        type="button"
        aria-label={open ? "Close menu" : "Open menu"}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="relative grid size-9 cursor-pointer place-items-center rounded-md text-fg-muted transition-colors hover:bg-subtle hover:text-fg"
      >
        {open ? <X className="size-5" /> : <Menu className="size-5" />}
        {hasReviews && !open && <span className="absolute top-1.5 right-1.5 size-2 rounded-full bg-wait ring-2 ring-surface" />}
      </button>

      {open && (
        <nav role="menu" className={cn(MENU_PANEL, "right-0")}>
          {NAV.map(({ to, label, end, reviews }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              role="menuitem"
              onClick={close}
              className={({ isActive }) => cn(MENU_ITEM, "py-2", isActive ? "bg-subtle font-medium" : "text-fg-muted")}
            >
              {label}
              {reviews && <ReviewBadge />}
            </NavLink>
          ))}
          <NextCheck className="mt-1 border-t border-line px-2.5 pt-2.5 pb-1.5" />
        </nav>
      )}
    </div>
  );
}
