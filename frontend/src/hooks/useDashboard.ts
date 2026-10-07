import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export const useDashboard = () =>
  useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard, refetchInterval: 5_000 });
