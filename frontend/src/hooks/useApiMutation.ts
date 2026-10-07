import { useMutation, useQueryClient, type QueryKey } from "@tanstack/react-query";
import { toast } from "sonner";

import { errorMessage } from "@/lib/api";

interface Options<TData> {
  /** Query keys to refetch after success. */
  invalidates: QueryKey[];
  success?: string | ((data: TData) => string);
}

/** Mutation that refreshes the given queries on success and toasts on success/error. */
export function useApiMutation<TVars = void, TData = unknown>(
  fn: (vars: TVars) => Promise<TData>,
  { invalidates, success }: Options<TData>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: (data) => {
      invalidates.forEach((queryKey) => queryClient.invalidateQueries({ queryKey }));
      if (success) toast.success(typeof success === "function" ? success(data) : success);
    },
    onError: (error) => toast.error(errorMessage(error)),
  });
}
