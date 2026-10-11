import { Outlet } from "react-router";

import { AppFrame } from "@/components/layout/AppFrame";
import { MainNav } from "@/components/layout/MainNav";
import { MobileMenu } from "@/components/layout/MobileMenu";
import { NextCheck } from "@/components/layout/NextCheck";
import { WorkspaceSwitcher } from "@/components/workspace/WorkspaceSwitcher";

export function AppShell() {
  return (
    <AppFrame
      header={
        <>
          <WorkspaceSwitcher />
          <MainNav />
          <NextCheck className="ml-auto hidden shrink-0 rounded-full border border-line px-3 py-1 lg:inline-flex" />
          <MobileMenu />
        </>
      }
    >
      <Outlet />
    </AppFrame>
  );
}
