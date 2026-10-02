# Student Guide — LinkedIn AI Copilot

Time needed: **10 minutes to set up**, then **about 15 minutes per working day**.

## 1. First run (10 minutes)

1. Open your copilot folder in Claude Code (see `START-HERE.md`, or the README if you installed the plugin).
2. Type `/linkedin-copilot`.
3. Claude asks which sources you have. Give as many as you can:
   - **Upwork profile** — Claude reads it through the Upwork connector (read-only).
   - **Résumé PDF** — give the file path, e.g. `C:\Users\...\Documents\Resume.pdf`.
   - **LinkedIn profile** — easiest: open your profile → *Resources* → *Save to PDF*, and give that file.
     Or sign in yourself in Claude's browser pane and Claude reads your own profile page once.
     **Never type your password into the chat.**
4. Claude researches and shows **3 ranked options** (roles or services) with evidence. Pick one —
   or ask to compare, see the evidence, or research another direction.
5. Claude sets up your campaign: profile improvements, first post drafts, a first list of people.
6. Say yes when Claude offers the **daily / weekly / monthly schedule**, then click **Run now** once on
   each scheduled task (sidebar → Scheduled) so it doesn't stop to ask for permissions later.

## 2. Every working day (~15 minutes)

At 08:30 the copilot prepares your drafts automatically (while the Claude app is open). Then:

1. Run `/linkedin-copilot`.
2. For each task, Claude shows **what, why, and the draft**, and opens the right LinkedIn page.
3. You **paste, check, and click** (Connect / Send / Post).
4. Type `done` — or `skip` if it doesn't feel right. Next task.

Got a reply? Type **"I got a reply"** and paste it. Claude pauses follow-ups and drafts your answer.
Someone said no? Paste it — Claude stops all contact with that person, permanently.

Only 5 minutes today? Say **"I have 5 minutes"** — you get the single most valuable task.

**Staying in touch.** Everyone you're building a relationship with has a warmth and a next-touch date:
hot (every 4 working days), warm (every 10), cold or "not now" (every 25). Claude drafts one *useful*
touch when it's due — a comment, congratulations on real news, a helpful article — never an empty
"just checking in". Paste "not now" replies and Claude brings that person back on the date they gave.
Ask **"who is going cold?"** any time.

## 3. Find jobs or win clients

**Career mode (LinkedIn job posts only)**
1. Claude prepares LinkedIn Jobs search links each day (your role, location, recent posts).
2. You open them and paste 2–5 posts that look right (link + job description).
3. Claude scores each post 0–100 against your real experience and names the gaps.
4. Claude tailors your résumé bullets and a short cover note, and finds people who could refer you.
5. You apply (Easy Apply or company site) and type **applied**.
6. Claude drafts a follow-up after 7 working days and prepares you for interviews.

**Business mode**
1. Claude builds your pitch kit: value statement, 30-second pitch, one-page offer, price options, objection answers.
2. Conversations that show a real need become deals with a dated next step.
3. Claude drafts the discovery invite, questions and the proposal; you send it and type **sent**.
4. You tell Claude when a deal is won or lost. No pitching in first messages.

## 4. Weekly and monthly (automatic)
- **Friday 17:00** — weekly review: what worked, the bottleneck, new people, next week's posts.
- **1st of the month** — re-reads your Upwork profile, refreshes research, re-checks your profile.
Big changes (a new direction) are always offered as options. **You decide.**

## 5. Settings — just say it
"Give me 20 minutes a day" · "Only 2 posts a week" · "Turn off follow-up drafts" ·
"Switch to business mode" · "Only remote jobs" · "Aim for 10 applications a week". Claude updates `linkedin-copilot/settings/PREFERENCES.md`.

## 6. Your dashboard
Open `linkedin-copilot/dashboard/index.html` in your browser: today's tasks with copy buttons,
your prospects, conversations, posts, opportunities and progress. It refreshes after every session.

## 7. Do's and don'ts (protect your LinkedIn account)

| ✅ Do | ❌ Don't |
| --- | --- |
| Read every draft before sending; edit it in your voice | Ask Claude to click Send/Connect/Post for you |
| Confirm only things that are true about you | Let anything claim results you didn't achieve |
| Send a few thoughtful messages a day | Mass-send or install "LinkedIn automation" extensions |
| Tell Claude when someone says no | Contact people again after they declined |

LinkedIn bans bots and automation, even in your own browser. The copilot is designed so that **you**
do every action on LinkedIn — that is what keeps your account safe.

## 8. FAQ / troubleshooting
- **"python is not recognized"** → install Python from python.org (tick *Add to PATH*), restart Claude.
- **Scheduled run didn't happen** → the Claude app must be open; missed runs run when you reopen it.
- **Upwork import failed** → add the Upwork connector, or paste your Upwork profile text instead.
- **Something looks wrong in my data** → say "check my copilot data". Backups are kept automatically
  in `linkedin-copilot/data/.backups/`.
- **Update to a new version** → see *Updating* in `START-HERE.md` (kit) or run `/plugin marketplace update stw-courses` (plugin). Your settings and data are kept.
