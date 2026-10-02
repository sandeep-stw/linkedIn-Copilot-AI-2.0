---
name: li-sales-pitch
description: "LinkedIn Copilot (business mode): build the offer and pitch kit (value statement, 30-second pitch, one-page offer, price options, objection answers) and run the sales pipeline from conversation to discovery call to proposal to close, drafting each step for the user to send. Use daily in business mode, or when the user asks how to pitch, sell, write a proposal, or answer an objection."
cadence: "Daily (step 2, business mode) + Weekly (pitch kit review)"
feature: sales_pitch
covers: "Sales extension (pitch kit + pipeline)"
---

# Sales pitch and pipeline

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md`. Cadence: Daily (step 2, business mode) + Weekly (pitch kit review).

Runs only when `mode: business` and `sales_pitch: on`. Selling happens **after** a real
conversation shows a need — no cold pitching (`immediate_pitch: off` stays respected). The student
sends every message and proposal; Claude never does.

## 1. Pitch kit (once after selection; refreshed weekly)
Build from the selected recommendation, validation findings (if any) and confirmed proof
(projects, results, testimonials the student confirms). Save each as `content` records:
- `kind: pitch_kit` — one-line value statement (who + problem + outcome), 30-second pitch,
  3 proof points (confirmed only), the ideal buyer, and the "not for" list.
- `kind: one_pager` — problem, approach, deliverables, timeline, price options, next step.
- Price options: 3 tiers (small pilot / standard / extended) as **hypotheses** — label them so
  until a buyer pays. Never invent market rates; cite a source or say "assumption".
- `kind: objection_answers` — honest answers to: too expensive, no time now, we do it in-house,
  need to ask my boss, send me something. Each ends with a low-pressure next step.
Show the kit side by side for approval; claims needing confirmation are highlighted.

## 2. Pipeline (deals)
A deal starts when a conversation shows a concrete need (from `interactions`, a reply, or a
meeting note). Create a `deals` record: `prospectId`, `offer`, `stage: conversation`, `nextStep`,
`nextStepDue`, `needEvidence` (quote or summary of what they said).

| Stage | What Claude prepares | Moves on when the student says |
| --- | --- | --- |
| conversation | A helpful reply + one question about the problem | they described the problem |
| discovery | Invitation to a 20-min call + discovery questions (reuse product-validation guide) + meeting prep | call happened (notes pasted) |
| proposal_drafted | `content` `kind: proposal` (`dealId`): their words for the problem, scope, timeline, price option, next step | "sent" → `proposal_sent` + `confirmationSource` |
| proposal_sent | Follow-up after `deal_follow_up_business_days`, with one useful addition | they replied |
| negotiation | Answers from objection_answers, adjusted scope options | agreement |
| won / lost | `won`: `outcomeEvidence` in the student's words; `lost`: reason | — |

Every open deal always has `nextStep` + `nextStepDue` (the store enforces it). Use
`status.dealsDue` daily. Contact tasks use types `pitch`, `sales_follow_up`, `send_proposal`
(do-not-contact applies automatically).

## 3. Daily
Draft the next step for each due deal (max `max_tasks_per_session` overall), and spot new deal
candidates in the latest replies. Keep stated interest separate from commitment: only a confirmed
"yes" with scope/price is `won`.

## Weekly
Pipeline review: deals per stage, stalled deals (no movement 2+ weeks), win/loss reasons. Refine
the pitch kit from what buyers actually said; log changes as `decisions`.

## Never
Pitch in a first message, send anything, invent testimonials/results/clients, present a price
as validated before someone paid, or keep pursuing a buyer who declined (decline → DNC).

## Completion criteria
Pitch kit approved; every open deal has a dated next step with a ready draft; won/lost recorded
only from the student's confirmation.
