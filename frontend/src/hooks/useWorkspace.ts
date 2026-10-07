import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { useApiMutation } from "@/hooks/useApiMutation";

export const useWorkspace = () => useQuery({ queryKey: ["workspace"], queryFn: api.workspace });

export const useUpdateWorkspace = () =>
  useApiMutation(api.updateWorkspace, { invalidates: [["workspace"]], success: "Settings saved" });
