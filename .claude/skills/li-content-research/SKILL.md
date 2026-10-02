---
name: li-content-research
description: "LinkedIn Copilot: plan the weekly LinkedIn content calendar and prepare post drafts up to the weekly quota. Use daily to top up drafts, weekly to plan the calendar, or when the user asks for a post."
cadence: "Daily (step 5) + Weekly (step 4)"
feature: content_research (ideas/calendar), post_drafting (drafts)
covers: FR-06, FR-07, AC-05, AC-08, AC-17
---

# Content research and post drafts

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Daily (step 5) + Weekly (step 4).

## Inputs
Campaign audience and goal; prior `content` records (avoid repeats); `post_drafts_per_week`;
research records; user-confirmed achievements only.

## Steps
1. Count drafts created this ISO week. Prepare only up to `post_drafts_per_week`.
2. Pick topics. Career: project lessons, technical demonstrations, architecture decisions, leadership.
   Business: buyer problems, workflows, evidence, case studies, useful answers. Skip topics used
   in the last 4 weeks.
3. Write each `content` record: `audience`, `objective`, `hook`, `body`, `cta`, `visualBrief`,
   `evidenceRefs`, `claimsToVerify`, `plannedFor` (date), `status: drafted`.
4. Create a task `type: publish_post`, `feature: post_drafting`, `dedupeKey: post:<YYYY-Www>:<n>`,
   `draftRef: <content id>`, `estMinutes: 5`.

## Rules
No fabricated anecdotes, no engagement bait ("comment YES"), no confidential client details,
no generic praise. If a story needs a detail you don't have, leave `[[confirm: …]]` placeholders
and list them in `claimsToVerify`.

## Lifecycle
drafted → approved (user OK'd text; still unpublished) → completed only when the user says they
published it; store the post URL in `publicationEvidence` if given, else `"user_confirmed"`.
Analytics are user-entered or unknown — never guessed.

## Permitted actions
Drafting and records. There is no publish button; the user posts manually.

## Failure behaviour
post_drafting off → ideas only, no draft tasks; existing draft tasks are paused.

## Completion criteria
This week's drafts exist up to the configured count, each with a publish task.
