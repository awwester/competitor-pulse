import { useParams } from "react-router";

import { RunView } from "@/components/runs/RunView";

export function RunDetailPage() {
  const { runId = "" } = useParams();
  return <RunView runId={runId} />;
}
