import { Play } from "lucide-react";
import { useNavigate } from "react-router";

import { Button } from "@/components/ui/Button";
import { useDashboard } from "@/hooks/useDashboard";
import { useCanWrite } from "@/hooks/useMeta";
import { useCreateRun } from "@/hooks/useRuns";

export function RunNowButton() {
  const canWrite = useCanWrite();
  const navigate = useNavigate();
  const createRun = useCreateRun();
  const hasPages = !!useDashboard().data?.pageCount;

  return (
    <Button
      disabled={!canWrite || !hasPages || createRun.isPending}
      onClick={() => createRun.mutate(undefined, { onSuccess: (run) => navigate(`/runs/${run.id}`) })}
    >
      <Play className="size-4" /> Run check now
    </Button>
  );
}
