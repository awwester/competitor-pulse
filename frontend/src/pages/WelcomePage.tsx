import { useNavigate } from "react-router";

import { NewCompanyForm } from "@/components/workspace/NewCompanyForm";

/** First run, before any company exists. */
export function WelcomePage() {
  const navigate = useNavigate();

  return (
    <section className="card mx-auto max-w-2xl p-6 animate-rise sm:p-10">
      <p className="eyebrow mb-3">Welcome</p>
      <h1 className="text-3xl font-semibold tracking-tight text-balance">Track what your competitors change</h1>
      <p className="mt-3 mb-8 max-w-prose text-sm text-fg-muted">
        Enter your company's website. The agent reads it, writes your company profile and suggests
        the competitors worth watching. You approve the list, then it watches their pricing,
        changelog and careers pages and briefs you on the changes that matter.
      </p>
      {/* The company list refetches with the new company, which replaces this screen. */}
      <NewCompanyForm onCreated={() => navigate("/")} />
      <p className="mt-6 border-t border-line pt-4 text-xs text-fg-faint">
        Prefer sample data without running any agents? Run{" "}
        <code className="font-mono text-fg-muted">make seed</code>, then reload.
      </p>
    </section>
  );
}
