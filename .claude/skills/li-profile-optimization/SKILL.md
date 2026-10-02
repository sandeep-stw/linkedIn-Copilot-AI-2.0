---
name: li-profile-optimization
description: "LinkedIn Copilot: audit the user's LinkedIn profile against the selected goal and draft headline/About/experience/skills proposals side by side, flagging claims to confirm. Use after selection, when the user asks to improve their LinkedIn profile, or for the monthly re-audit."
cadence: "Setup + Monthly (step 3)"
feature: profile_optimization
covers: FR-05
---

# Profile optimisation

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Setup + Monthly (step 3).

## Inputs
Active campaign + selected recommendation; current profile text (user pasted, or résumé as proxy —
say so); research records about target roles/buyers.

## Steps
1. If current profile text is missing, ask the user to paste headline + About (one request, offer
   to proceed from the résumé meanwhile).
2. Produce proposals, each a `tasks` record of `type: profile_edit`, `feature: profile_optimization`:
   headline (3 options), About, top 3 experience rewrites, skill priority list, Featured
   recommendations, banner copy, 1–2 recommendation-request drafts, credibility gaps.
3. Each proposal stores `current`, `proposed`, `claimsToConfirm` (every metric, title, certification,
   or responsibility not in the user's materials), `rationale`, and `proposalState`:
   drafted → approved → applied | skipped.
4. Show current vs proposed side by side, claims highlighted. Ask the user to confirm claims before
   marking approved.

## Rules
Never manufacture metrics, certifications, endorsements, or responsibilities. Keep the user's voice.

## Permitted actions
Drafting and task records only. The user edits LinkedIn.

## Failure behaviour
No profile text → work from résumé and label proposals "based on résumé, not live profile".

## Completion criteria
All proposals exist with states; `applied` only after the user says they applied it
(`completionEvidence` = their words).
