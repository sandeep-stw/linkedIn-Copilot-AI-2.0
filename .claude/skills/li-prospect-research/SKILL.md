---
name: li-prospect-research
description: "LinkedIn Copilot: define the ideal audience and build/expand a scored, deduplicated prospect shortlist from permitted sources, with LinkedIn search links the user runs. Use weekly to top up the shortlist, or when the user asks who to connect with."
cadence: "Weekly (step 2)"
feature: prospect_research
covers: FR-08, FR-09, FR-10, AC-10
---

# Prospect research and qualification

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Weekly (step 2).

## Inputs
Campaign, selected recommendation, `prospect_target`, `initial_shortlist`, `activity_recency_days`.

## Steps
1. **Audience design (once per campaign, saved on the campaign record as `audience`):** ideal people,
   companies, exclusions, search terms, qualification criteria and category mix.
   Career mix: hiring_manager, recruiter, senior_peer, referral_contact, community_connector.
   Business mix: decision_maker, operational_champion, partner, industry_connector.
2. **Acquire candidates** from public company pages, team pages, talks, articles, user-provided
   lists or pasted excerpts. Where direct collection isn't possible, create a task
   `type: run_search` with a ready LinkedIn search URL and the exact filters, and ask the user to
   paste back names/headlines/URLs of the best results.
3. **Write `prospects`**: `name`, `role`, `company`, `geography`, `category`, `source`
   (url | user_supplied | user_pasted_search), `linkedinUrl` (only if verified), `fitReason`,
   `evidence`, `evidenceDate`, `confidence`, `activityStatus`, `activityEvidence`,
   `relationshipStage: shortlisted`, `doNotContact: false`, `fitScore` (0–100) + `scoreExplanation`.
4. **Dedupe** by normalised LinkedIn URL (lowercase, strip query and trailing slash). Same name +
   company but no URL → set `possibleDuplicateOf` and ask; never auto-merge.
5. **Rank** by audience fit (40), need/opportunity evidence (30), relationship context (20),
   activity confidence (10). Explain the score. A high score is not proof of authority or intent.
6. Start with `initial_shortlist` strong candidates; expand toward the target only after the first
   batch is being worked.

## Rules
`activityStatus: active` only with a dated observed post/comment within the recency window
(the store rejects it otherwise). Default `unknown`. Never scrape LinkedIn or claim full coverage.

## Completion criteria
Shortlist saved with sources and scores; every shortlisted prospect has a next action or a
`run_search` task is pending.
