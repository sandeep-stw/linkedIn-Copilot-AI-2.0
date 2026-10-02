---
name: li-product-validation
description: "LinkedIn Copilot: run the ten-person product validation interview campaign (business mode) — invitations, discussion guide, findings, and continue/narrow/revise/pause recommendation."
cadence: "Daily (step 3, business mode) + Monthly (step 4)"
feature: validation_interviews
covers: FR-13, FR-14, AC-15
---

# Product validation (10 conversations)

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Daily (step 3, business mode) + Monthly (step 4).

## Inputs
Business campaign, one defined segment, prospects in that segment, `validation_participants`.

## Steps
1. Recommend `validation_participants` people from ONE segment. Create `interviews` records
   (`schedulingState: proposed`, `notesProvenance: none`) with `role`, `problemExperience`,
   `buyingInfluence` (or "unknown").
2. Draft invitations (via li-relationship-guidance rules) — ask for advice, not a sale.
3. Prepare the discussion guide (default questions below) before any major build is proposed.
4. After each conversation the user pastes notes → `notesProvenance: user_notes`, extract
   `findings` (problem instances, frequency, cost, workaround, who approves spend, priority triggers,
   pilot criteria) and `commitments` (stated interest vs. paid/committed — keep separate).
5. After ≥5 and again at 10: synthesise into a `research` record + `decisions` proposal:
   repeated problems, concrete examples, workarounds, existing spend, decision process,
   contradictions, pilot commitments → recommend continue | narrow segment | revise offer |
   research further | pause, with supporting AND opposing evidence. Ten interviews are
   directional, not proof of demand.

## Default questions
1. Tell me about the last time this problem occurred. 2. How do you handle it today?
3. Who participates in the process? 4. How often does it happen? 5. What time, cost, delays, or
errors does it create? 6. What have you already tried? 7. What worked and what did not?
8. Who approves spending to improve it? 9. What would make it a priority now?
10. What would a small pilot need to demonstrate for you to consider it?

## Completion criteria
10 interviews tracked; summary distinguishes repeated evidence, contradictions and next experiment;
the user selects the decision (major change rule).
