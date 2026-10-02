# Skill run protocol (every `li-*` skill and runner follows this)

## 1. Bootstrap
0. If `linkedin-copilot/` doesn't exist in the project yet, the skill's own bootstrap line
   (`install.py`) creates it — every `li-*` skill runs that line before reading this file.
1. From the project root: `python linkedin-copilot/tools/store.py init` (no-op if already set up).
2. `python linkedin-copilot/tools/store.py status` — the JSON drives what you do.
3. Read `linkedin-copilot/instructions/CAMPAIGN-MANAGER.md` and `LINKEDIN-POLICY-GUARDRAILS.md`.
   Read `RESEARCH-RULES.md` when the skill researches.

## 2. Gate
- The skill's `feature:` switch (frontmatter) is `off` in PREFERENCES.md → skip with a one-line
  reason. `core` skills always run.
- No active campaign (`stage` = onboarding_*) → only `li-profile-intake` and
  `li-opportunity-research` may run; every other skill reports "awaiting onboarding" and stops.

## 3. Interactive vs scheduled
| | Interactive (user present) | Scheduled / unattended |
| --- | --- | --- |
| Questions | Max 2 decision-changing ones | None — leave an `awaiting_user` task instead |
| Browser / LinkedIn | Open ONE page per task, per guardrails | **Never** |
| Upwork connector | Read-only calls | Read-only calls (monthly re-sync only) |
| Records | Drafts + user-confirmed completions | Drafts and prepared tasks only, never `completed` |
| Selections / major changes | Present options, user picks | Write a `pendingDecision` task, don't decide |

A run is **scheduled** when invoked by a runner (`li-daily`, `li-weekly`, `li-monthly`) or the
prompt says scheduled / unattended.

## 4. Run log (standalone runs and runners)
- Runner jobs: `run start --job <li-daily|li-weekly|li-monthly> --period <day|week|month>`.
  Exit 4 = already done or running for this period → stop silently.
- When a runner calls a component skill, the component does NOT start its own run log.
- Finish with `run finish --job … --period … --note "<step results>"`, or `run fail`.

## 5. Finish
Everything is written through `store.py` (validation, provenance, dedupe). Then
`python linkedin-copilot/tools/store.py dashboard`. Output: what changed, and the single next
action for the user.
