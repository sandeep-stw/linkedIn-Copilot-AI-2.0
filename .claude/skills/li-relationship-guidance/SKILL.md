---
name: li-relationship-guidance
description: "LinkedIn Copilot: choose the next genuine interaction for each shortlisted prospect and draft connection notes, comments, messages, referral requests and meeting prep. Use daily, or when the user asks what to send someone."
cadence: "Daily (step 4)"
feature: relationship_guidance (choice of action), connection_drafting (drafts)
covers: FR-11, FR-12, FR-16
---

# Relationship guidance and personalised drafts

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Daily (step 4).

## Inputs
Prospect record + history (`interactions`), campaign goal, any post/context the user pasted,
Communication preferences.

## Next best action (pick one per prospect)
substantive comment · relevant question · contextual connection request · requested resource ·
advice conversation · referral request · discovery invitation · collect more context first.
An explicit request for help or open opportunity justifies an immediate relevant response — no
artificial warm-up sequence required.

## Drafting
- Create an `interactions` record `direction: outgoing`, `status: drafted`, `type`, `content`,
  `relevanceReason`, and a matching task (`dedupeKey: <type>:<prospectId>`, `linkedinUrl` if known,
  `estMinutes` 2–5).
- Length: keep connection notes short (check LinkedIn's current note limit; if unsure, ≤ 200 chars).
- Tone per preferences; `immediate_pitch: off` means no selling in a first message.
- Never invent mutual connections, familiarity, quotes from posts, or past interactions. Without
  real context, write a truthful neutral note or create a `collect_context` task instead.

## Meetings (meeting_preparation)
Before: context, 5 questions, desired outcome, notes template (task `type: meeting_prep`).
After the user pastes notes: save `interactions` `type: meeting_note`, `direction: incoming`,
`notesProvenance: user_notes`; extract commitments; draft the follow-up; create `opportunities` for
referrals/interviews/proposals. AI summaries stay `ai_summary_unconfirmed` until the user confirms.

## Permitted actions
Drafts and records only. User sends in LinkedIn and confirms.

## Completion criteria
Each targeted prospect has one prepared, explained next action; DNC prospects have none.
