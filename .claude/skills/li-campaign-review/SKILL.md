---
name: li-campaign-review
description: "LinkedIn Copilot: weekly/monthly review — outcome metrics with denominators, bottleneck diagnosis, tactic changes, and options for major direction changes. Use on review day or when the user asks how the campaign is going."
cadence: "Weekly (step 1) + Monthly (step 5)"
feature: weekly_review
covers: FR-18, Section 18 metrics, AC-16
---

# Campaign review

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Weekly (step 1) + Monthly (step 5).

## Inputs
All data files for the review period (default: last 7 days in the configured timezone).

## Metrics (write `metrics` records)
Career: relevant conversations, referral offers, qualified opportunities, interviews, offers.
Business: qualified conversations, completed discovery interviews, repeated-problem evidence,
pilot discussions, paid pilots, revenue.
Supporting: invitation acceptance rate, reply rate — each with `numerator`, `denominator`,
`period`, `calculation`, `source` (computed | user_entered | integration_confirmed | unknown).
Drafts never count as sent. Unknown → `numerator: null`, `source: unknown` — never 0.

## Diagnosis (pick the real bottleneck, don't just add volume)
low audience fit · weak evidence/positioning · irrelevant openings · unclear urgency ·
poor role/offer alignment · too much workload for the time budget · not enough sends confirmed.

## Actions
- Tactic change (within the selected goal) → apply, and write a `decisions` record
  (`owner: ai`, `reason`, `evidenceRefs`, `reviewDate`, `affectedTasks`).
- Major change (goal, role, segment, offer) → present 2–3 options with evidence; the user selects.
  Never reverse a user-selected goal because of one weak week.
- Refresh stale research that still drives decisions.

## Output to user
5-line summary: outcomes, bottleneck, what changed, what you need from them, next week's focus.

## Completion criteria
Metrics saved with denominators; one diagnosed bottleneck; changes logged as decisions.
