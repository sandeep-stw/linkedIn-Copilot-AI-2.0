# LinkedIn AI Copilot

An AI-first copilot for LinkedIn that runs inside Claude Code. Tell it about yourself once — through
your **Upwork profile**, **résumé PDF** or **LinkedIn profile** — and it researches your best options,
lets you pick one, then prepares your LinkedIn actions every day. You stay in control of every send.

## Requirements
- Claude desktop app (Code tab) or Claude Code CLI
- Python 3.9 or newer (`python --version`) — install from python.org if missing
- Optional: the Upwork connector (to import your Upwork profile)

## Install

**Option A — from GitHub (recommended, gets updates)**
```
/plugin marketplace add <owner>/<repo>
/plugin install linkedin-copilot@stw-courses
```

**Option B — from the zip your instructor gave you**
1. Unzip `linkedin-copilot-v<version>.zip` somewhere permanent (e.g. `Documents/claude-plugins`).
2. In Claude Code: `/plugin marketplace add <path-to>/stw-courses`
3. `/plugin install linkedin-copilot@stw-courses`

Then create (or open) an empty folder for your campaign — e.g. `Documents/my-linkedin` — open it in
Claude Code, and run:
```
/linkedin-copilot:linkedin-copilot
```

## Skills

| Cadence | Command | What it does |
| --- | --- | --- |
| Start here | `/linkedin-copilot:linkedin-copilot` | Setup on first run, daily session after; also `done`, `skip`, `reply`, `review`, `settings` |
| Setup | `/linkedin-copilot:li-profile-intake` | Reads Upwork profile, résumé PDF, your own LinkedIn profile |
| Setup | `/linkedin-copilot:li-opportunity-research` | 3 ranked options → you choose → campaign created |
| Setup | `/linkedin-copilot:li-profile-optimization` | Profile improvements, side by side |
| Daily | `/linkedin-copilot:li-daily` | Runs the daily routine below, in order |
| Daily 1 | `/linkedin-copilot:li-follow-up-management` | Follow-ups, replies, declines |
| Daily 2 | `/linkedin-copilot:li-job-search` | Career: LinkedIn job posts → fit score → tailored application → follow-up → interview prep |
| Daily 2 | `/linkedin-copilot:li-sales-pitch` | Business: pitch kit and deals from conversation to close |
| Daily 3 | `/linkedin-copilot:li-relationship-guidance` | Next action + message draft per person |
| Daily 4 | `/linkedin-copilot:li-product-validation` | Interview invites (business mode) |
| Daily 5 | `/linkedin-copilot:li-content-research` | Post drafts |
| Daily 6 | `/linkedin-copilot:li-tracker-management` | Today's plan + dashboard |
| Weekly | `/linkedin-copilot:li-weekly` | Review → job search or sales pipeline → new prospects → next week's posts |
| Weekly 1 | `/linkedin-copilot:li-campaign-review` | Results, bottleneck, adjustments |
| Weekly 2 | `li-job-search` / `li-sales-pitch` | Tune job search filters, or review deals and the pitch kit |
| Weekly 3 | `/linkedin-copilot:li-prospect-research` | More people to connect with |
| Monthly | `/linkedin-copilot:li-monthly` | Upwork re-sync → research refresh → profile re-check → monthly review |

## Safety and LinkedIn policy
LinkedIn forbids bots and automation that send, connect, post or scrape — even in your own logged-in
browser. This copilot never does those things: it prepares everything and opens the right page; you
paste and click. Scheduled runs never touch LinkedIn. See `STUDENT-GUIDE.md` for the details.

## Your data
Everything stays on your computer in `<your campaign folder>/linkedin-copilot/` (settings in Markdown,
records in JSON, a dashboard in HTML). No passwords or cookies are stored. Updating the plugin never
overwrites your settings or data.
