---
name: li-tracker-management
description: "LinkedIn Copilot: the only way campaign state changes — confirm done/skip with provenance, build today's time-boxed plan, apply feature switches, log runs, and render the dashboard. Use when the user says done/skip/sent/posted, and at the end of every run."
cadence: "Daily (step 7, always last) + Weekly + Monthly (last step)"
feature: core
covers: FR-17, FR-19, Section 16, AC-04..AC-07, AC-11..AC-13, AC-18
---

# Tracker management

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Daily (step 7, always last) + Weekly + Monthly (last step).

All commands run from the project root: `python linkedin-copilot/tools/store.py <cmd>`.

## Writing records
1. Write the JSON record(s) to a scratch file (or pipe via stdin with `--file -`).
2. `python linkedin-copilot/tools/store.py upsert <file> --file <path> [--expect-revision N]`.
3. Exit 2 = validation failed (fix the record, don't bypass). Exit 3 = conflict (re-read with
   `get`, merge, retry once; if it conflicts again tell the user). Never edit JSON by hand.

Every record needs `provenance` (`ai`, `user`, `user_supplied`, `scheduler`, or a source URL);
`campaignId` where relevant. Timestamps are added automatically (UTC).

## Task shape
```json
{"campaignId":"c_0001","type":"connection_note","feature":"connection_drafting","title":"Send note to A. Rao",
 "reason":"Leads platform team at target employer; posted about hiring 2026-09-28","priority":2,
 "estMinutes":3,"status":"prepared","dueDate":"2026-10-03","relatedIds":["p_0004","i_0009"],
 "dedupeKey":"connection_note:p_0004","linkedinUrl":"https://www.linkedin.com/in/...","draft":"..."}
```
Priority 1 = highest. Status flow: pending → prepared → awaiting_user → completed | skipped;
plus paused, blocked (`blockedReason`), cancelled.

## Confirming user actions ("done t_0012", "I sent it", "posted")
Update exactly once, in this order:
1. `interactions` (or `content`) → `status: completed`, `confirmationSource: user_confirmed`,
   `occurredAt` (now unless the user gave a time).
2. `tasks` → `status: completed`, `completionEvidence: "user said: <their words>"`.
3. `prospects` → advance `relationshipStage` with a `stageReason` (the store records history and
   refuses jumps to connected+ without a completed interaction), set `nextActionId`.
   `lastTouchAt` / `touchCount` / `nextTouchDue` update automatically from the interaction.
"Approved" or "looks good" is approval, NOT completion.

## Feature switches
After any feature change: `python linkedin-copilot/tools/store.py apply-features` (pauses queued tasks of
disabled features; lists paused tasks to reassess when re-enabled — reassess before resuming).

## Session start
`python linkedin-copilot/tools/store.py status [--minutes N]` → use `todayPlan`, `nextAction`, `followups`,
`pendingDecisions`, `staleResearch`, `preferenceIssues`, `dataProblems`, `recentFailures`.

## Scheduled runs
`run start --job daily-prep` (exit 4 = already done/running today → stop silently),
then `run finish` or `run fail --note "<reason>"`. Background runs prepare work only.

## Always finish with
`python linkedin-copilot/tools/store.py dashboard`.
