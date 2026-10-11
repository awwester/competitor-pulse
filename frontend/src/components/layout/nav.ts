export interface NavItem {
  to: string;
  label: string;
  end?: boolean;
  /** Shows the count of runs awaiting review next to the label. */
  reviews?: boolean;
}

export const NAV: NavItem[] = [
  { to: "/", label: "Brief", end: true },
  { to: "/runs", label: "Runs", reviews: true },
  { to: "/competitors", label: "Competitors" },
  { to: "/settings", label: "Settings" },
];
