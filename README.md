# LinkedIn Copilot AI 2.0

AI-first LinkedIn career & sales copilot built as Claude Code skills. It builds options from an
Upwork profile, résumé PDF and LinkedIn profile, lets the user pick a direction, then prepares
daily, weekly and monthly actions that the user completes in LinkedIn (policy-safe,
browser-assisted — nothing is sent or posted automatically).

## Repository layout

| Path | What |
| --- | --- |
| `.claude/skills/linkedin-copilot` | Entry skill — run `/linkedin-copilot` |
| `.claude/skills/li-daily` · `li-weekly` · `li-monthly` | Scheduled runners (ordered steps) |
| `.claude/skills/li-*` | 13 component skills (intake, research, profile, content, prospects, relationships, nurture, job search, sales pitch, validation, follow-ups, review, tracker) |
| `linkedin-copilot/instructions/` | Operating rules, research rules, LinkedIn policy guardrails, run protocol |
| `linkedin-copilot/settings/PREFERENCES.md` | Single source of settings |
| `linkedin-copilot/tools/store.py` | Validated JSON storage layer + dashboard renderer |
| `linkedin-copilot/tools/install.py` | Installs/upgrades the working folder (never touches settings/data) |
| `docs/` | Student-facing docs shipped in packages |
| `package.config.json` · `make-student-package.bat` | Build config for the clean Student Kit / plugin |
| `PLAN.md` · `CHANGELOG.md` | Implementation plan and release notes |

## Use it yourself
Open this folder in Claude Code and run `/linkedin-copilot`.
Requires Python 3.9+. Campaign data is created in `linkedin-copilot/data/` and is git-ignored.

## Build the student package
Run `/student-package` in Claude Code, or double-click `make-student-package.bat`.
Output (git-ignored): `dist/LinkedIn-Copilot-Student-Kit-v<version>.zip` and a plugin build.
The build engine lives in the user-level `package-product` skill (`~/.claude/skills/package-product`).
