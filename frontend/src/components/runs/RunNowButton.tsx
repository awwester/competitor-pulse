import { Play } from "lucide-react";
import { useNavigate } from "react-router";

import { Button } from "@/components/ui/Button";
import { useCanWrite } from "@/hooks/useMeta";
import { useCreateRun } from "@/hooks/useRuns";

export function RunNowButton() {
  const canWrite = useCanWrite();
  const navigate = useNavigate();
  const createRun = useCreateRun();

  return (
    <Button
      variant="signal"
      disabled={!canWrite || createRun.isPending}
      onClick={() => createRun.mutate(undefined, { onSuccess: (run) => navigate(`/runs/${run.id}`) })}
    >
      <Play className="size-4" /> Run check now
    </Button>
  );
}
