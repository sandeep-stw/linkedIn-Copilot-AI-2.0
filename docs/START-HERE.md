# {{NAME}} — Student Kit v{{VERSION}}

## Start in 3 steps

1. **Move this folder** somewhere permanent, e.g. `Documents/{{KIT_FOLDER}}`
   (this folder becomes your personal campaign — your settings and progress are saved here).
2. **Open it in Claude:** Claude desktop app → *Code* tab → choose this folder.
   (CLI: open a terminal in this folder and run `claude`.)
3. **Type:** `/linkedin-copilot`

Claude asks which of these you have — your **Upwork profile**, **résumé PDF**, **LinkedIn profile** —
then researches and shows you 3 options to choose from. That's it.

Needs **Python 3.9+** (`python --version`). Missing? Install it from python.org and tick *Add to PATH*.

## What's inside

| Path | What it is |
| --- | --- |
| `START-HERE.md` | This page |
| `STUDENT-GUIDE.md` | Daily routine, settings, do's & don'ts, FAQ |
| `.claude/skills/` | The copilot's skills (don't edit) |
| `linkedin-copilot/settings/PREFERENCES.md` | Your settings — or just tell Claude in plain words |
| `linkedin-copilot/dashboard/index.html` | Your dashboard (appears after the first session) |
| `linkedin-copilot/data/` | Your private campaign data (created on first run) |

## Updating to a new kit version
Unzip the new kit anywhere, then in Claude (inside your **current** campaign folder) say:
*"Update my copilot from `<path to the new kit folder>`"* — or run
`python "<new kit folder>/linkedin-copilot/tools/install.py" .`
Your settings and data are kept; only the skills, instructions and tools are refreshed.

## Privacy
Everything stays on your computer. No passwords or cookies are stored. Don't share your
`linkedin-copilot/data/` folder.
