import { Stat } from "@/components/ui/Stat";
import { formatDuration, formatTokens, formatUsd } from "@/lib/format";
import type { RunSummary } from "@/types/api";

export function RunStats({ run }: { run: RunSummary }) {
  const totalInput = run.inputTokens + run.cacheReadTokens + run.cacheWriteTokens;
  const cacheRate = totalInput ? Math.round((run.cacheReadTokens / totalInput) * 100) : 0;

  return (
    <div className="card grid grid-cols-2 gap-6 p-5 sm:grid-cols-3 lg:grid-cols-6">
      <Stat label="Pages checked" value={run.pagesChecked} />
      <Stat label="Changed" value={run.pagesChanged} />
      <Stat label="Duration" value={formatDuration(run.startedAt, run.finishedAt)} />
      <Stat label="Agent turns" value={run.numTurns} />
      <Stat
        label={`Tokens · ${cacheRate}% cached`}
        value={formatTokens(totalInput + run.outputTokens)}
      />
      <Stat label="Cost" value={formatUsd(run.costUsd)} />
    </div>
  );
}
