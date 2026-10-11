# Ideas: More Ways to Track Competitors

Today every signal comes from tracked pages (pricing, changelog, blog, homepage, careers, docs): each check snapshots them and diffs against the previous run. These are candidate ways to widen that. None are built yet. Screenshot diffs are already on the [roadmap](../README.md#roadmap).

## New sources of signal

### Fits the existing crawl → diff → analyst pipeline

- **New pages from `sitemap.xml` and RSS/Atom.** Diff the list of URLs, not the page text. A new `/solutions/healthcare` or `/vs/<us>` page often appears before any tracked page changes. New URLs could also feed page discovery.
- **Hiring from public job boards.** Greenhouse, Lever and Ashby serve job boards as JSON. That is more structured than the careers page, and open roles show strategy months before a launch ("four ML engineers and a Head of EMEA Sales").
- **Status-page incidents.** Statuspage-style JSON endpoints list outages. "Three incidents this month" is useful to sales.
- **Release feeds.** GitHub releases for developer-tool competitors, and App Store release notes from the iTunes lookup API.
- **New subdomains from certificate-transparency logs** ([crt.sh](https://crt.sh)). A certificate for `beta-ai.competitor.com` can show up before the product is announced.

### Higher value, harder to get

- **Review sites** (G2, Capterra): their terms forbid scraping and they block bots.
- **LinkedIn and X:** the APIs are closed or expensive.
- **Ad libraries** (Meta, Google Ads Transparency): show which messaging is being tested, but are awkward to crawl.
- **Funding data:** Crunchbase is paid.
- **News and Hacker News mentions:** the HN Algolia API is free, but news in general is noisy.

## New uses for existing findings

- **Agent-maintained battlecards.** A living document per competitor (positioning, pricing, strengths, weaknesses, recent moves) that an agent updates from each approved run's findings. The agent would keep this memory across runs, building on the existing human review.
- **Structured history.** Extract price points and plan names as data, so pricing can be shown as a timeline instead of a stream of findings.
- **Periodic strategy synthesis.** A monthly or quarterly "what is this competitor doing?" brief written across all of a competitor's findings, not one run's diff.

## Likely next steps

1. **Battlecards.** Biggest payoff, with no new data source.
2. **Hiring signals.** Brings in a small source abstraction (page, feed, jobs API) that the other sources can reuse.
3. **Sitemap new-page detection.** The smallest change; stays inside the current pipeline.
