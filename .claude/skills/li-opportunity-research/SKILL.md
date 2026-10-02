---
name: li-opportunity-research
description: "LinkedIn Copilot: research career roles or business offers from the user's profile, present 3 ranked evidenced options for the user to select, and create the campaign from the selection. Monthly: refresh stale research and check the selected direction still holds (propose only)."
cadence: "Setup + Monthly (step 2)"
feature: career_research (career) | offer_research (business)
covers: FR-01, FR-02, FR-03, FR-04, AC-01, AC-02, AC-03, AC-14
---

# Opportunity research

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Setup + Monthly (step 2).

## Inputs
- Whatever the user has given: résumé, profile text, portfolio, website, service list, or one sentence.
- PREFERENCES.md: `mode`, `recommendation_options`, `target_geography`, `research_before_asking`.

## Steps
1. **Start from the li-profile-intake record** (Upwork / résumé PDF / LinkedIn — see
   `/li-profile-intake`). If none exists, run li-profile-intake first. Don't re-ask for
   anything already extracted.
2. **If mode is unclear**, infer it from the materials and say which you assumed; don't ask.
3. **Research** (follow RESEARCH-RULES.md). Use web search/fetch if available.
   - Career: current listings and employer career pages for 4–6 candidate roles; keep the best 3.
   - Business: 4–6 candidate offers from the user's capabilities; keep the best 3.
   Save each finding as a `research` record. Tag the batch with `researchVersion: "rv_YYYYMMDD"`.
4. **Write `recommendations`** (one per option, `selectionState: proposed`):
   - Career fields: `option` (role), `responsibilities`, `fit`, `gaps`, `employers`, `locations`,
     `workArrangement`, `compensation` (only if sourced, base vs total), `preparation` (steps + effort
     + assumptions), `confidence`, `openQuestions`, `evidenceRefs` (research ids), `rank`, `rankReason`.
   - Business fields: `option` (offer), `segment`, `problem`, `alternatives`, `differentiation`,
     `deliveryScope`, `commercialAssumptions` (price = hypothesis), `validationExperiment`, plus the same
     confidence/evidence/rank fields.
5. **Selection cards.** Present each option compactly: rank, one-line why, fit, biggest gap,
   confidence, evidence count. Offer: *Select N*, *Show evidence N*, *Compare*, *Research another direction*.
   Recommend one. Ask at most 1–2 decision-changing questions (e.g. relocation, notice period) only if
   they would change the ranking.

## Selection (user picks)
1. Update chosen rec → `selected`, others → `rejected`; record `selectedAt`, `selectionRationale`.
2. Write a `decisions` record (`owner: user`, `change`, `reason`, `evidenceRefs`).
3. Create the `campaign` record: `mode`, `goal`, `selectedRecommendationId`, `successMeasures`,
   `milestones` (3–5), `constraints`, `priorities`, `blockers`, `evidenceGaps`, `stage: "positioning"`,
   `status: active`, `prospectTarget` (from prefs). Any other active campaign → `paused`.
4. Hand off to li-tracker-management to create the first tasks (profile audit, first content draft,
   first shortlist search).

## Permitted actions
Web research, reading user files, writing research/recommendations/decisions/campaign records.

## Failure behaviour
No search tools or sources fail → explain the gap, build options from the user's materials with
`confidence: low`, mark which evidence is missing, and still present options (AC-14).

## Completion criteria
3 ranked, evidenced options shown (before any long questionnaire); after selection, campaign +
milestones + first tasks persisted.
