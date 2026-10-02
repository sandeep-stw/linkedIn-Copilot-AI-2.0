---
name: li-daily
description: "LinkedIn Copilot DAILY runner (Mon–Fri). Runs the daily skills in order — follow-ups, job search (career) or sales pipeline (business), relationship actions, validation (business mode), post drafts, today's plan + dashboard. Use for the scheduled daily prep, or when the user says 'run my daily LinkedIn prep'."
cadence: "Daily — working days, daily_prep_time (default 08:30)"
---

# Daily runner

First run `python "linkedin-copilot/tools/install.py" .`, then follow
`linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md`. This runner owns the run log;
component skills run inside it (read each `.claude/skills/<name>/SKILL.md` and follow it in this
same session — don't spawn agents).

## 0. Gate
1. `python linkedin-copilot/tools/store.py prefs` → if this is a scheduled run and
   `background_preparation` is `off`, or today isn't in `working_days`:
   `run skip --job li-daily --period day --note "<reason>"` (ignore exit 4) and stop.
2. `run start --job li-daily --period day` → exit 4 = already ran/running today → stop silently.
3. `status` → if `stage` is onboarding_*: `run finish --job li-daily --period day --note "awaiting onboarding"`, stop.

## Steps (in this order; a failing step is noted and the runner continues)

| # | Skill | Why this position | Daily scope |
| --- | --- | --- | --- |
| 1 | `li-follow-up-management` | Replies/declines change everything after | Process `followups`; draft due follow-ups; pause after max unanswered; DNC on declines |
| 2a | `li-job-search` | Career mode: jobs are the goal | Today's LinkedIn Jobs search links; drafts for `jobFollowups`; apply tasks for shortlisted posts |
| 2b | `li-sales-pitch` | Business mode: deals are the goal | Next-step drafts for `dealsDue`; new deal candidates from recent replies |
| 3 | `li-relationship-guidance` | Uses the updated relationship state | Next action + draft for the top shortlisted prospects without one (cap at `max_tasks_per_session`) |
| 4 | `li-product-validation` | Only when `mode: business` and feature on | Invites/follow-ups for proposed interviews; skip otherwise |
| 5 | `li-content-research` | After contact work (lower urgency) | Top up drafts only if this week is below `post_drafts_per_week`; one draft per day max |
| 6 | `li-tracker-management` | Always last | `apply-features`, `status` → today's plan within `minutes_per_day`, `dashboard` |

Run 2a only in career mode and 2b only in business mode.

## Finish
`run finish --job li-daily --period day --note "fu:<n> jobs:<n> deals:<n> drafts:<n> posts:<n> tasks today:<n>"`
(or `run fail` with the failing step). Output a 3-line brief: prepared items, the first task for
the user (with time estimate), anything awaiting their decision.

Scheduled runs never open LinkedIn or mark anything sent/completed.
