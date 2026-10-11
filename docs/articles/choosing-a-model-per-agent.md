# Not every job needs the biggest model

[Competitor Pulse](https://github.com/awwester/competitor-pulse) runs three AI agents:

- **The analyst** reads what changed on competitors' websites, decides which changes matter to your business, and writes the weekly brief.
- **Company discovery** reads your website, drafts a profile of your company and suggests competitors to watch.
- **Page discovery** looks over each competitor's site and picks the pages worth watching, such as pricing and changelogs.

All three ran on Claude Opus, the most capable model we had. That was the easy default, but it raised a question: does picking a handful of pages really need the same model as judging what a competitor's price cut means for you?

## Letting the tests decide

The project already had a set of tests (evals) that run the real agents on fixed scenarios and check what they do. There are nine of them: a competitor cuts its price, another repositions for a new market, routine bug fixes that shouldn't be flagged, two pages hiding instructions that try to trick the agent, and the two discovery jobs.

We ran the full set three times, once on each of Claude's three model sizes:

| Model | Passed | Cost of the full run |
| --- | --- | --- |
| Opus (largest) | 9 of 9 | Baseline |
| Sonnet (middle) | 9 of 9 | About 2.5x cheaper |
| Haiku (smallest) | 9 of 9 | About 15x cheaper |

## Every model passed, so where did they differ?

A pass rate alone doesn't separate them, so we looked at what each agent actually did.

- **The analyst** gave the same verdicts on every model, and none of them fell for the trick pages. It stays on Opus anyway. Judging what matters is the core of the product, and nine tests aren't enough to show a smaller model would hold up on messy real websites.
- **Company discovery** found the two obvious competitors on every model. Only Opus searched the web and came back with a third real one. That extra find is the point of the job, so it stays on Opus.
- **Page discovery** picked exactly the same pages on all three models, so we moved it to Haiku.

## A small wobble, fixed in code

On a later run, Haiku picked the right pages but skipped writing a short note about who the competitor is. The analyst relies on that note. Instead of rewording the instructions and hoping, we changed the tool itself: it won't add a page until the note exists. When it refuses, the agent writes the note and carries on. Haiku then passed five runs out of five.

## The result

Page discovery is now about 50x cheaper. The quality hasn't changed, and the jobs that need judgment still get the strongest model.

The bigger takeaway is the method. Instead of picking one model for everything, test each job on its own, compare what the agents actually did and not just whether they passed, and when a smaller model slips, fix the gap in code.

The code, the evals and the full results are in the [Competitor Pulse repo](https://github.com/awwester/competitor-pulse). The numbers behind this post are in [Eval results](../evals.md#choosing-a-model-per-agent).
