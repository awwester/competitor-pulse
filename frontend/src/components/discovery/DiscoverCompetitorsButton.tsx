import { Sparkles } from "lucide-react";
import { useNavigate } from "react-router";

import { Button } from "@/components/ui/Button";
import { useStartDiscovery } from "@/hooks/useDiscovery";
import { useCanWrite } from "@/hooks/useMeta";

/** Re-run competitor discovery from the saved company website, e.g. to find newcomers. */
export function DiscoverCompetitorsButton({ website }: { website: string }) {
  const canWrite = useCanWrite();
  const navigate = useNavigate();
  const start = useStartDiscovery();

  return (
    <Button
      variant="outline"
      disabled={!canWrite || start.isPending}
      onClick={() => start.mutate(website, { onSuccess: (run) => navigate(`/runs/${run.id}`) })}
    >
      <Sparkles className="size-4" /> Find more competitors
    </Button>
  );
}
