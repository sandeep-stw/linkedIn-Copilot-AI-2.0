---
name: li-weekly
description: "LinkedIn Copilot WEEKLY runner. Runs in order — campaign review (metrics + bottleneck), job search or sales pipeline review, relationship (nurture) review, prospect shortlist top-up, next week's content calendar, then plan + dashboard. Use for the scheduled weekly run or when the user asks for the weekly LinkedIn review/planning."
cadence: "Weekly — weekly_review_day at weekly_review_time (default Friday 17:00)"
---

# Weekly runner

First run `python "linkedin-copilot/tools/install.py" .`, then follow
`linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md`. This runner owns the run log;
components run inside it in this same session.

## 0. Gate
1. `run start --job li-weekly --period week` → exit 4 = already done this ISO week → stop silently.
2. `status` → onboarding_* → `run finish --job li-weekly --period week --note "awaiting onboarding"`, stop.

## Steps (review → adjust → refill)

| # | Skill | Weekly scope |
| --- | --- | --- |
| 1 | `li-campaign-review` | Last 7 days: metrics with denominators, one bottleneck, tactic changes logged as decisions, options (not changes) for major moves. Skip only if `weekly_review: off` |
| 2 | `li-job-search` (career) / `li-sales-pitch` (business) | Career: which search keywords produced good posts, adjust filters, applications vs `applications_per_week`. Business: pipeline review, stalled deals, refresh the pitch kit from what buyers said |
| 3 | `li-nurture` | Relationship review: who warmed up, who is going cold, who has no plan, stage hygiene; top 3 relationships for next week |
| 4 | `li-prospect-research` | Apply the review's findings: top up the shortlist toward `initial_shortlist` → `prospect_target` (only if this week's list is being worked); refresh search links; re-check activity evidence older than `activity_recency_days` → `unknown` |
| 5 | `li-content-research` | Plan next week's calendar (topics + `plannedFor` dates) up to `post_drafts_per_week`; draft the first one |
| 6 | `li-tracker-management` | `apply-features`, close stale tasks (overdue > 10 business days → ask, don't delete), `dashboard` |

## Finish
`run finish --job li-weekly --period week --note "<bottleneck>; prospects +<n>; posts planned <n>"`.
Output the 5-line review summary (outcomes, bottleneck, what changed, what's needed from the
user, next week's focus).
