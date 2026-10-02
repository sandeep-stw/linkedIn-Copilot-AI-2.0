# LinkedIn AI Copilot — Implementation Plan

Source of truth: `LinkedIn_AI_Copilot_Requirements.md` v1.0 (2 Oct 2026).
Runtime: Claude Code desktop app (skills + scheduled tasks + built-in browser + Upwork MCP).

## How it works (one picture)

```
 Upwork MCP ─┐                                   ┌─> dashboard/index.html (read-only snapshot)
 Résumé PDF ─┼─> profile-intake ─> opportunity-research ─> 3 ranked options ─> YOU SELECT
 LinkedIn   ─┘   (own profile, you sign in)                          │
                                                                    v
        campaign + plan ─> daily prep (scheduled 08:30 Mon–Fri) ─> drafts + tasks
                                                                    │
     /linkedin-copilot daily ─> Claude opens ONE LinkedIn page ─> you paste + click ─> "done"
                                                                    │
                       store.py records it (provenance) ─> follow-ups, weekly review, tactics
```

## User effort (target)

| When | You do | Time |
| --- | --- | --- |
| Once | Run `/linkedin-copilot`, name your sources (Upwork / résumé path / LinkedIn), pick 1 of 3 options | 10 min |
| Once | Approve profile changes, apply them in LinkedIn | 15 min |
| Daily | `/linkedin-copilot` → per task: paste, click, say `done` | 15 min (configurable) |
| On reply | Paste the reply, say "I got a reply" | 1 min |
| Weekly | Read the 5-line review, pick an option if a big change is proposed | 3 min |

## LinkedIn policy position

All browser use follows `linkedin-copilot/instructions/LINKEDIN-POLICY-GUARDRAILS.md`:
Claude opens the single page a task needs, during your live session. **You** type/paste and click
every Connect / Send / Post. No scraping, no bulk page opening, and no LinkedIn access from scheduled
runs. Fully automated sending or posting would breach LinkedIn's User Agreement §8.2 and puts the
account at risk, so it is deliberately not offered. The only sanctioned automation path is the
official Share on LinkedIn API, for posting only (Phase 4).

## Skills (all callable as /commands and schedulable)

| Cadence | Order | Skill | Job |
| --- | --- | --- | --- |
| Entry | — | `/linkedin-copilot` | One command for everything: setup first time, daily session after |
| Setup | 1 | `/li-profile-intake` | Upwork (connector) · résumé PDF · LinkedIn own profile |
| Setup | 2 | `/li-opportunity-research` | 3 ranked options → user selects → campaign |
| Setup | 3 | `/li-profile-optimization` | Profile proposals side by side |
| **Daily** | runner | `/li-daily` | Runs D1–D5 in order |
| Daily | D1 | `/li-follow-up-management` | Due follow-ups, replies, declines |
| Daily | D2 | `/li-relationship-guidance` | Next action + draft per prospect |
| Daily | D3 | `/li-product-validation` | Interview invites (business mode) |
| Daily | D4 | `/li-content-research` | Top up post drafts to the weekly quota |
| Daily | D5 | `/li-tracker-management` | Today's plan, feature switches, dashboard |
| **Weekly** | runner | `/li-weekly` | Runs W1–W4 in order |
| Weekly | W1 | `/li-campaign-review` | Metrics, bottleneck, tactic changes |
| Weekly | W2 | `/li-prospect-research` | Shortlist top-up, activity re-check |
| Weekly | W3 | `/li-content-research` | Next week's calendar |
| Weekly | W4 | `/li-tracker-management` | Stale tasks, dashboard |
| **Monthly** | runner | `/li-monthly` | Runs M1–M6 in order |
| Monthly | M1 | `/li-profile-intake` | Upwork re-sync (read-only) |
| Monthly | M2 | `/li-opportunity-research` | Research refresh; direction check (propose only) |
| Monthly | M3 | `/li-profile-optimization` | Profile re-audit |
| Monthly | M4 | `/li-product-validation` | Interview synthesis (business mode) |
| Monthly | M5 | `/li-campaign-review` | Month-over-month review |
| Monthly | M6 | `/li-tracker-management` | Validate, retention list, backups, dashboard |

## Files

```
.claude/skills/            linkedin-copilot (entry) · li-daily · li-weekly · li-monthly · 10 li-* skills
linkedin-copilot/
  instructions/  CAMPAIGN-MANAGER.md · RESEARCH-RULES.md · LINKEDIN-POLICY-GUARDRAILS.md · SKILL-RUN-PROTOCOL.md
  settings/      PREFERENCES.md        (only settings source; edit by hand or in plain words)
  data/          12 JSON files (schemaVersion + revision) + .backups/ (last 30 revisions each)
  tools/store.py validated storage layer: atomic writes, revision conflicts, dedupe, DNC
                 cascade, feature pausing, business-day follow-ups, day/week/month run log, dashboard
  dashboard/     index.html (regenerated after every session/run)
```

## Phases and status

### Phase 1 — Foundation ✅ built
- [x] Markdown settings with validation; plain-language `set-pref` that keeps other Markdown (AC-06)
- [x] JSON data contracts for all 11 entities + run log; IDs, provenance, UTC timestamps, cross-refs
- [x] Atomic writes, file lock, revisions + conflict exit code (AC-13), backups + `restore`
- [x] Business rules enforced in the store: completion needs evidence (AC-07/08), active needs dated
      evidence (AC-10), DNC blocks contact tasks and cancels open ones (AC-09), feature-off pauses (AC-05),
      unknown metrics never 0, single active campaign, task dedupe
- [x] Session-start `status`: next action, time-boxed plan (AC-11), follow-ups, stale research, failures
- [x] Dashboard: 10 views, escaped output, copy buttons, Open LinkedIn, unknown shown as unknown
- [x] Onboarding from Upwork MCP / résumé PDF / LinkedIn own profile → 3 options → selection (AC-01..03)

### Phase 2 — Daily ownership ✅ playbooks built, validate with real use
- [x] Profile proposals, content drafts, prospect qualification, relationship drafts, follow-ups
- [x] Browser-assisted daily walk-through (one page per task)
- [ ] First real campaign cycle end to end: research → selection → action → confirmed → next recommendation

### Phase 3 — Outcome improvement ✅ playbooks built
- [x] Ten-person validation, meeting notes → commitments, opportunities, metrics, weekly review

### Phase 4 — Optional (not built; verify first)
- [ ] Interactive dashboard (local file service so Mark done/Skip/Settings save without chat)
- [ ] Share on LinkedIn API (OAuth, posting only) as an opt-in publish path
- [ ] Notifications/reminders outside the app; retention purge job; multi-user isolation

### Phase 5 — Student package (next)
Goal: a student installs once, runs `/linkedin-copilot`, and is onboarded in ~10 minutes.
- [x] Portable: no hard-coded paths or connector ids in skills; timezone set from the system clock
- [x] Personal data excluded (`.gitignore`: data, backups, inputs, rendered dashboard)
- [x] **Student Kit** (default): `/student-package` or double-click `make-student-package.bat`
      → `dist/LinkedIn-Copilot-Student-Kit-v<version>.zip` (unzip → open folder → `/linkedin-copilot`)
- [x] Clean gates on every build: leak scan, forbidden-file audit, skill checks, smoke test incl. upgrade, MANIFEST.json (sha256)
- [x] Package as a Claude Code plugin with the reusable `/package-product` skill
      (`package.config.json` → `dist/stw-courses/` marketplace + `dist/linkedin-copilot-v<version>.zip`)
- [x] Template installer (`tools/install.py`): first-run install + upgrades that never touch settings/data
- [x] Neutral defaults (timezone UTC, career mode), README, STUDENT-GUIDE, CHANGELOG
- [x] Build gates: leak scan (emails, connector ids, personal paths), skill frontmatter, smoke test in a clean folder
- [ ] Run `claude plugin validate dist/stw-courses` (CLI not on PATH yet) and test-install it yourself
- [ ] Pilot with 2–3 students; collect friction points before wider release
- [ ] Push `dist/stw-courses` to a private GitHub repo → students run `/plugin marketplace add <owner>/<repo>`
- [ ] Release flow: `/package-product release patch|minor|major`

## Scheduling (FR-19)

| Scheduled task | When | Runs |
| --- | --- | --- |
| 1. LinkedIn – DAILY | Mon–Fri 08:30 | `/li-daily` — drafts/tasks only; skips if `background_preparation: off` (AC-18), non-working day, or already ran |
| 2. LinkedIn – WEEKLY | Fri 17:00 | `/li-weekly` |
| 3. LinkedIn – MONTHLY | 1st of month 09:00 | `/li-monthly` |

Scheduled runs happen only while the Claude desktop app is open; missed runs execute on next launch.
Last successful run and failures appear in `status` and on the dashboard.

## Commands you might use

```
/linkedin-copilot              start (onboards first time, daily session afterwards)
/linkedin-copilot done t_0007  confirm you did it in LinkedIn
/linkedin-copilot reply        paste a reply you received
/linkedin-copilot review       progress + bottleneck now
/linkedin-copilot settings 20 minutes a day, turn off post drafting
```
