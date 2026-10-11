import { Plus } from "lucide-react";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Select, UrlInput } from "@/components/ui/Field";
import { useAddPage } from "@/hooks/useCompetitors";
import { PAGE_TYPES, type PageType } from "@/types/api";

export function AddPageForm({ competitorId }: { competitorId: string }) {
  const addPage = useAddPage(competitorId);
  const [adding, setAdding] = useState(false);
  const [url, setUrl] = useState("");
  const [pageType, setPageType] = useState<PageType>("pricing");

  if (!adding) {
    return (
      <Button variant="ghost" size="sm" className="mt-3" onClick={() => setAdding(true)}>
        <Plus className="size-3.5" /> Track a page
      </Button>
    );
  }

  const close = () => {
    setUrl("");
    setAdding(false);
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    addPage.mutate({ url, pageType }, { onSuccess: close });
  };

  return (
    <form onSubmit={submit} className="flex flex-wrap gap-2 pt-4">
      <UrlInput
        required
        autoFocus
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://competitor.com/pricing"
        className="min-w-0 flex-1 basis-64"
      />
      <Select value={pageType} onChange={(e) => setPageType(e.target.value as PageType)} className="w-36">
        {PAGE_TYPES.map((type) => (
          <option key={type} value={type}>{type}</option>
        ))}
      </Select>
      <Button type="submit" variant="outline" disabled={addPage.isPending}>
        <Plus className="size-4" /> Track page
      </Button>
      <Button type="button" variant="ghost" onClick={close}>
        Cancel
      </Button>
    </form>
  );
}
