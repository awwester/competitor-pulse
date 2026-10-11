import { Sparkles } from "lucide-react";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { UrlInput } from "@/components/ui/Field";
import { useCanWrite, useMeta } from "@/hooks/useMeta";

interface DiscoveryFormProps {
  initial?: string | null;
  pending: boolean;
  onSubmit: (website: string) => void;
}

/** The company website discovery starts from, with the local sample company one click away. */
export function DiscoveryForm({ initial, pending, onSubmit }: DiscoveryFormProps) {
  const canWrite = useCanWrite();
  const { data: meta } = useMeta();
  const [website, setWebsite] = useState(initial ?? "");
  const sample = meta?.sampleCompanyUrl;

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit(website);
  };

  return (
    <form onSubmit={submit} className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <UrlInput
          required
          aria-label="Company website"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
          placeholder="yourcompany.com"
          className="min-w-0 flex-1 basis-72"
        />
        <Button type="submit" disabled={!canWrite || !meta?.agentConfigured || pending}>
          <Sparkles className="size-4" /> Discover competitors
        </Button>
      </div>
      {sample && (
        <p className="text-xs text-fg-faint">
          No site handy?{" "}
          <button
            type="button"
            onClick={() => setWebsite(sample)}
            className="cursor-pointer underline underline-offset-4 hover:text-fg"
          >
            Try the sample company
          </button>
          , Tallybird, with fictional competitors served locally.
        </p>
      )}
    </form>
  );
}
