import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export const useMeta = () => useQuery({ queryKey: ["meta"], queryFn: api.meta, staleTime: Infinity });

/** False in the hosted read-only demo; UI hides or disables mutating controls. */
export function useCanWrite(): boolean {
  const { data } = useMeta();
  return data ? !data.demoMode : false;
}
