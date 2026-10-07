import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Field, Input, Textarea } from "@/components/ui/Field";
import type { CompetitorInput } from "@/types/api";

interface CompetitorFormProps {
  initial?: CompetitorInput;
  submitLabel: string;
  pending: boolean;
  onSubmit: (values: CompetitorInput) => void;
  onCancel: () => void;
}

const EMPTY: CompetitorInput = { name: "", website: "", notes: "" };

export function CompetitorForm({ initial = EMPTY, submitLabel, pending, onSubmit, onCancel }: CompetitorFormProps) {
  const [values, setValues] = useState(initial);
  const set = (key: keyof CompetitorInput) => (e: { target: { value: string } }) =>
    setValues((v) => ({ ...v, [key]: e.target.value }));

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit(values);
  };

  return (
    <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
      <Field label="Name">
        <Input required value={values.name} onChange={set("name")} placeholder="Ledgerly" />
      </Field>
      <Field label="Website">
        <Input required type="url" value={values.website} onChange={set("website")} placeholder="https://ledgerly.com" />
      </Field>
      <div className="sm:col-span-2">
        <Field label="Notes" hint="Optional context for you. The agent sees findings, not these notes.">
          <Textarea rows={2} value={values.notes} onChange={set("notes")} />
        </Field>
      </div>
      <div className="flex gap-2 sm:col-span-2">
        <Button type="submit" disabled={pending}>{submitLabel}</Button>
        <Button type="button" variant="ghost" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  );
}
