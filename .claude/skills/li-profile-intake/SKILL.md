---
name: li-profile-intake
description: "LinkedIn Copilot: import the user's starting evidence from Upwork profile (Upwork connector), résumé PDF, and their own LinkedIn profile, and merge it into one profile extraction. Use for first-time setup, when the user shares a résumé/Upwork/LinkedIn profile, or for the monthly Upwork re-sync."
cadence: "Setup + Monthly (step 1)"
feature: core
covers: FR-01
---

# Profile intake (Upwork · Résumé PDF · LinkedIn)

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Setup + Monthly (step 1).

Ask ONE question to start: *"Which do you have — Upwork profile, résumé PDF, LinkedIn profile?
Any combination works."* Then use every source the user names. More sources = better options.

## Source A — Upwork profile (Upwork MCP)
1. Find the Upwork connector tools with ToolSearch query `+upwork profile` (server ids differ per
   install), then load `get_profile`, `get_freelancer_dashboard`, `list_contracts`. No Upwork
   connector → point the student to the connector directory to add it, or use the fallback below.
2. Read-only calls only: `get_profile` (title, overview, skills, rate, portfolio, employment,
   certifications), optionally `get_freelancer_dashboard` / `list_contracts` for job success,
   completed work and client industries. Never call update/send/submit tools here.
3. Upwork earnings, job success and reviews count as **supported** evidence (platform data);
   overview text counts as **user-stated**.
4. MCP unavailable or not connected → tell the user, offer the alternative: paste the Upwork
   profile text or a PDF export.

## Source B — Résumé (PDF file)
1. Ask for the path (e.g. `C:\Users\...\Resume.pdf`) or a file in the project folder.
2. Read it with the Read tool (use `pages` for >10 pages). Scanned/image PDF with no text →
   use the `anthropic-skills:pdf` skill for OCR, or ask for a text copy.
3. Copy the file into `linkedin-copilot/inputs/` only if the user agrees (keeps the campaign
   reproducible); otherwise just reference the path.
4. Résumé contents are **user-stated** until supported or confirmed.

## Source C — LinkedIn profile (user logs in; own profile only)
Recommended first, because it needs no automation on LinkedIn:
- **Save to PDF:** on their own profile, *Resources → Save to PDF*, then treat it as Source B.

If the user prefers the browser session:
1. Open the built-in browser at `https://www.linkedin.com/login` (load the
   `anthropic-skills:built-in-browser` skill first).
2. Say: *"Please sign in yourself in the browser pane. I won't type or see your password.
   Tell me when you're on your profile page."* Never enter credentials, never complete a CAPTCHA.
3. When the user confirms, read ONLY their own profile page (`/in/me/`) as text with
   `get_page_text` — one read, plus the "see all" pages for Experience/Skills only if the user
   opens them. No clicking that changes anything, no other people's profiles, no search pages,
   no messaging, no feed crawling, no repeated or scheduled access.
4. Tell the user once: LinkedIn restricts automated access, so this is a one-time read of their
   own page at their request; Save-to-PDF is the zero-risk route.
5. Never store cookies, session data, or credentials. Leave the session as is — don't sign out.

## Merge and save
1. Build one extraction: experience, skills, industries, achievements, delivery capabilities,
   proof assets (portfolio, case studies, reviews), constraints (location, availability, rate).
2. For each fact record `sources: [upwork|resume|linkedin]` and `userStated|supported`.
   Flag conflicts between sources (different titles/dates/metrics) as `conflicts` — ask the user
   to resolve only the ones that would change a recommendation.
3. Save as a `research` record: `question: "Profile intake"`, `source` = list of sources used,
   `observedAt` = today, `confidence`, `facts`, `conflicts`, `currentLinkedinProfile` (headline +
   About text, if available — used later by li-profile-optimization).
4. Infer `mode` (career vs business): Upwork-heavy freelancer evidence → suggest **business**
   (selling services) or career — state the assumption and let the selection cards decide.
   Update via `set-pref mode <value>` only after the user picks a direction.

## Completion criteria
At least one source ingested and saved; conflicts listed; handed to li-opportunity-research.
