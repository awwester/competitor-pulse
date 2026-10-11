import { NavLink } from "react-router";

import { NAV } from "@/components/layout/nav";
import { ReviewBadge } from "@/components/layout/ReviewBadge";
import { cn } from "@/lib/format";

/** Inline header links from `sm` up; `MobileMenu` takes over below that. */
export function MainNav() {
  return (
    <nav className="hidden min-w-0 gap-1 overflow-x-auto sm:flex">
      {NAV.map(({ to, label, end, reviews }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            cn(
              "shrink-0 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              isActive ? "bg-subtle text-fg" : "text-fg-muted hover:text-fg",
            )
          }
        >
          {label}
          {reviews && <ReviewBadge />}
        </NavLink>
      ))}
    </nav>
  );
}
