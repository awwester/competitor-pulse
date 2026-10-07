import { Plus } from "lucide-react";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Field";
import { useAddSuggestion } from "@/hooks/useDiscovery";

const EMPTY = { name: "", website: "" };

/** A competitor the agent missed, added during review. */
export function AddSuggestionForm({ runId }: { runId: string }) {
  const add = useAddSuggestion(runId);
  const [values, setValues] = useState(EMPTY);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    add.mutate(values, { onSuccess: () => setValues(EMPTY) });
  };

  return (
    <form onSubmit={submit} className="flex flex-wrap gap-2 border-t border-line px-5 py-4">
      <Input
        required
        value={values.name}
        onChange={(e) => setValues((v) => ({ ...v, name: e.target.value }))}
        placeholder="Missing one? Name"
        className="min-w-0 flex-1 basis-40"
      />
      <Input
        required
        type="url"
        value={values.website}
        onChange={(e) => setValues((v) => ({ ...v, website: e.target.value }))}
        placeholder="https://competitor.com"
        className="min-w-0 flex-[2] basis-56"
      />
      <Button type="submit" variant="outline" disabled={add.isPending}>
        <Plus className="size-4" /> Add
      </Button>
    </form>
  );
}
