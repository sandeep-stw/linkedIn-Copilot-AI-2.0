---
name: li-monthly
description: "LinkedIn Copilot MONTHLY runner. Runs in order — Upwork profile re-sync, market/opportunity research refresh, profile re-audit, validation synthesis (business), monthly review, housekeeping + dashboard. Use for the scheduled monthly run or when the user asks for a monthly LinkedIn strategy check."
cadence: "Monthly — monthly_review_day at monthly_review_time (default 1st at 09:00)"
---

# Monthly runner

First run `python "linkedin-copilot/tools/install.py" .`, then follow
`linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md`. This runner owns the run log;
components run inside it in this same session.

## 0. Gate
1. `run start --job li-monthly --period month` → exit 4 = already done this month → stop silently.
2. `status` → onboarding_* → `run finish --job li-monthly --period month --note "awaiting onboarding"`, stop.

## Steps (refresh evidence → re-check direction → re-position → review)

| # | Skill | Monthly scope |
| --- | --- | --- |
| 1 | `li-profile-intake` | **Upwork re-sync only** (read-only connector): new reviews, contracts, skills since last intake → new `research` record. Résumé/LinkedIn only if the user dropped a new file in `linkedin-copilot/inputs/`. Never open LinkedIn |
| 2 | `li-opportunity-research` | Refresh `staleResearch` behind the selected direction; check current listings/demand. If the direction looks weaker, create recommendations + an `awaiting_user` decision task — **never change the goal** |
| 3 | `li-profile-optimization` | Re-audit proposals against new evidence (new projects, reviews, skills); new proposals as drafts |
| 4 | `li-product-validation` | Business mode only: synthesise interviews so far → continue/narrow/revise/research/pause proposal |
| 5 | `li-campaign-review` | Monthly period: month-over-month metrics, tactic changes that worked or not (review dates due) |
| 6 | `li-tracker-management` | Housekeeping: `validate`; list records past `retention_days` and ask before deleting; confirm backups exist; `dashboard` |

## Finish
`run finish --job li-monthly --period month --note "<summary>"`. Output: what changed in the
evidence, whether the direction still holds (with confidence), profile updates to approve, and
any decision waiting for the user.
