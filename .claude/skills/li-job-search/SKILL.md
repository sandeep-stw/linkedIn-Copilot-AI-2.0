---
name: li-job-search
description: "LinkedIn Copilot (career mode): find jobs from LinkedIn job posts only — build LinkedIn Jobs search links the student opens, score the posts they paste, tailor résumé bullets and a cover note, find referral contacts, track applications to offer, and prepare interviews. Use daily in career mode, or when the user asks to find jobs, apply, or prepare for an interview."
cadence: "Daily (step 2, career mode) + Weekly (search refresh)"
feature: job_search
covers: "Job search extension (LinkedIn job posts only)"
---

# Job search (LinkedIn job posts only)

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md`. Cadence: Daily (step 2, career mode) + Weekly (search refresh).

Runs only when `mode: career` and `job_search: on`. **Source: LinkedIn job posts only** — no other
job boards, no Upwork. Follow `LINKEDIN-POLICY-GUARDRAILS.md` §Jobs: Claude never loads or reads
LinkedIn search results or job pages; the student opens them and pastes what they want assessed.

## 1. Search links (daily, ~1 min for the student)
1. From the campaign's selected role(s), locations and constraints, pick 1–3 keyword sets
   (e.g. the role title + one key skill; a common alternative title).
2. For each: `python linkedin-copilot/tools/store.py jobs-url --keywords "<kw>" --location "<place>"`
   (filters come from the Jobs section of PREFERENCES.md: date posted, workplace, experience).
3. Create one task `type: run_job_search`, `feature: job_search`, `dedupeKey: jobsearch:<YYYY-MM-DD>`,
   `estMinutes: 5`, with the links in `draft` and this instruction for the student:
   *"Open each link, open the 2–5 posts that look right, and paste each post here (the URL plus the
   job description text — Ctrl+A, Ctrl+C on the post page is fine)."*

## 2. Assess pasted posts
For each post the student pastes:
1. Save a `jobs` record: `title`, `company`, `location`, `workplace`, `postingUrl` (must be a
   linkedin.com/jobs URL; the store dedupes by LinkedIn job id), `postedText` (trimmed),
   `requirements` (must-have vs nice-to-have), `stage: found`, `source: linkedin_job_post`.
2. Score `fitScore` 0–100 against the student's **verified** profile (intake record): must-have
   skills 50, seniority/scope 20, domain 15, location/eligibility 15. Write `fitReason` and `gaps`.
   Never inflate: unverified skills don't count.
3. `fitScore >= min_job_fit` → `stage: shortlisted`. Below → `closed` with the reason, unless the student
   insists.
4. Show a compact ranked list: score, why, biggest gap, recommended action.

## 3. Prepare the application (shortlisted → preparing)
For the student's top picks, up to `applications_per_week`:
- `content` `kind: resume_tailoring` (`jobId`): 4–6 rewritten résumé bullets mapped to the post's
  requirements, using only confirmed facts; list `claimsToVerify`.
- `content` `kind: cover_note` (`jobId`): ≤ 150 words, specific to the post, no generic praise.
- **Referral path:** from `prospects`, find people at that company (or ask the student to check
  "People you may know at <company>" themselves and paste names). Draft a short referral ask through
  `li-relationship-guidance` rules — honest about the relationship, never inventing familiarity.
- Task `type: apply_job`, `dedupeKey: apply:<jobId>`, `linkedinUrl: <postingUrl>`, `estMinutes: 10`:
  *"Open the post, apply (Easy Apply or the company site), paste the cover note, attach your résumé.
  Then tell me 'applied'."*

## 4. Track (only the student's words move stages)
- "Applied" → `stage: applied`, `appliedAt`, `confirmationSource: user_confirmed` (the store rejects it otherwise).
- `status.jobFollowups` (after `job_follow_up_business_days`) → draft a short follow-up to the recruiter
  or hiring manager if known (`type: job_follow_up`); set `lastFollowUpAt` when the student sends it.
- Recruiter reply / screening / interview / offer / rejection → update `stage`; record an
  `interactions` entry if a person is involved; create `opportunities` for interviews and offers.

## 5. Interview prep (stage screening/interviewing)
`content` `kind: interview_prep` (`jobId`): company snapshot from public sources, the post's top 5
requirements → STAR stories from the student's confirmed experience, 8 likely questions, 5 questions
to ask, a 30-second "why me". Task `type: interview_prep`.

## Weekly
Review the week's searches: which keyword sets produced shortlisted posts? Adjust keywords and
filters (log a `decisions` record), and report applications vs `applications_per_week`.

## Never
Load LinkedIn search/job pages yourself, click Apply/Easy Apply, submit applications, claim skills
the student hasn't confirmed, or mark anything applied without the student saying so.

## Completion criteria
Today's search links are prepared; every pasted post is scored and saved once; top picks have
tailored materials and an apply task; follow-ups due are drafted.
