---
name: li-nurture
description: "LinkedIn Copilot: nurture relationships over time and keep every prospect's status current — warmth (hot/warm/cold), useful touches on a cadence, 'not now' contacts brought back on their revisit date, going-cold alerts, and a recorded stage history. Use daily for touches due, weekly for the relationship review, or when the user asks who to stay in touch with, who is going cold, or to update someone's status."
cadence: "Daily (step 3) + Weekly (step 3)"
feature: nurture
covers: "Nurture + status maintenance extension"
---

# Nurture and status

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md`. Cadence: Daily (step 3) + Weekly (step 3).

Nurture = staying genuinely useful to people over time, so the relationship is warm when an
opportunity appears. Status = every person's stage, warmth and next touch always reflect what
actually happened. Status changes go through `store.py` only.

## Status model (enforced by store.py)
- **Stage** (`relationshipStage`): shortlisted → engaging → invited → connected → conversing →
  meeting → referral / opportunity; plus `paused` and `declined`.
  - Moving to connected or beyond needs a completed interaction with that person, or
    `stageEvidence` in the student's words (e.g. an existing 1st-degree connection).
  - Always pass `stageReason` when changing stage; the store appends `stageHistory`
    (from, to, when, by, reason) automatically. Never edit `stageHistory` yourself.
  - Only the student can move someone out of `declined`.
- **Nurture plan** (`nurtureTrack`): `none` · `active` · `long_term` (said "not now"; needs
  `revisitOn` and `notNowReason`).
- **Warmth** (`temperature`, required when nurtured):
  - **hot**: replying, a meeting is planned, or an open opportunity. Touch every `nurture_hot_business_days` (4).
  - **warm**: friendly, occasional replies. Touch every `nurture_warm_business_days` (10).
  - **cold**: no response yet, or a long-term contact. Touch every `nurture_cold_business_days` (25).
- **Touch tracking:** recording a completed outgoing interaction updates `lastTouchAt`,
  `touchCount` and `nextTouchDue` automatically; an incoming one updates `lastInboundAt`.

## Daily (from `status`)
1. **`nurtureDue`**: for each person (cap within `max_tasks_per_session` overall), draft ONE useful
   touch and create a task `type: nurture_touch`, `dedupeKey: nurture:<prospectId>:<nextTouchDue>`.
   The touch must give something. Choose by what is genuinely available:
   - a substantive comment on their recent post (only if the student pasted or saw it);
   - congratulations on real news (new role, launch, anniversary) that the student mentioned;
   - a relevant resource: an article, a template, or the student's own post that answers their problem;
   - a helpful intro, or an answer to something they asked earlier;
   - a short, specific check-in tied to the last conversation.

   Never send "just checking in" with nothing in it, never pitch, never invent news or quotes.
   No genuine material → create `collect_context` instead ("open their profile/activity and tell me
   one thing they posted").
2. **`revisitDue`** ("not now" people whose date arrived): draft a re-opener that references their
   reason ("you mentioned the hiring freeze until Q4…"). Set `nurtureTrack: active`, warmth from
   context (usually warm).
3. **Replies** (from follow-up-management): reply received → `temperature: hot`, stage forward with
   `stageReason`. Cool or short reply → `warm`. No reply after the follow-ups → `long_term` +
   `revisitOn` (+ cold cadence) instead of dropping them.

## Weekly relationship review
From `relationshipFunnel`, `goingCold`, `noNurturePlan`:
- **Warming up**: people who replied this week. Propose the next step (meeting, referral, deal).
- **Going cold** (no touch for 2× their cadence): one decision each. Touch now with something
  useful, move to `long_term` with a revisit date, or `paused` with a reason.
- **No plan**: real relationships (connected or beyond) with `nurtureTrack: none`. Assign a track and warmth.
- **Stage hygiene**: anyone stuck in one stage for 4+ weeks? Correct the stage (with `stageReason`)
  to what is true now.
- Report: counts per stage vs last week, people who moved forward, and the 3 most valuable
  relationships to invest in next week.

## "Not now" intake
When the student pastes "not now / maybe later / after X":
`nurtureTrack: long_term`, `notNowReason` (their words, short), `revisitOn` (their timing, or
`nurture_cold_business_days` ahead), `temperature: cold` or `warm`. Confirm in one line:
"Ravi: back on your list on 2027-01-05".

## Never
Nurture someone who declined or opted out. Fake familiarity. Send touches yourself. Change
stages without a reason, or invent interactions to justify a stage.

## Completion criteria
Every due touch has one prepared, useful draft. Revisit-date people are back in play. Every real
relationship has a track and warmth. Every stage change carries a reason in its history.
