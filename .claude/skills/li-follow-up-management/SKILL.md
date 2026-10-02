---
name: li-follow-up-management
description: "LinkedIn Copilot: find follow-ups due on the business-day cadence, draft them, handle 'I got a reply' intake, and stop all contact on a decline. Use daily, or when the user pastes a reply."
cadence: "Daily (step 1)"
feature: follow_up_drafting
covers: FR-15, AC-09
---

# Follow-up management

> **First:** run `python "linkedin-copilot/tools/install.py" .` (installs/upgrades the working folder;
> no-op when current), then follow `linkedin-copilot/instructions/SKILL-RUN-PROTOCOL.md` (bootstrap, feature switch, run log,
> interactive vs scheduled behaviour). Cadence: Daily (step 1).

## Inputs
`python linkedin-copilot/tools/store.py followups` output, interactions history, Follow-ups preferences.

## Cadence (defaults, configurable)
First follow-up 5 business days after the last outgoing message; second 7 more business days
later; after 2 unanswered follow-ups → pause the prospect. Business days use `working_days` and
`timezone`. Recipient timing ("ping me after the 15th") overrides cadence: store it in
`recipientTimingNote` and set the task `dueDate` accordingly.

## Handling `followups` actions
- `follow_up_N` → draft an `interactions` follow-up (adds something useful; never guilt-trips) +
  task `dedupeKey: followup:<prospectId>:<N>`.
- `pause` → prospect `relationshipStage: paused`, cancel open contact tasks.
- `reassess_reply` → ask the user what the reply said (if not already recorded), then route to
  li-relationship-guidance.

## "I received a reply" intake
1. Record `interactions` `direction: incoming`, `type: reply_received`, `status: completed`,
   `content` = what the user pasted/summarised, `occurredAt`.
2. Cancel queued follow-ups for that prospect (pause_on_reply).
3. Classify: positive / question / not now (timing) / decline / opt-out.
4. Decline or opt-out → also record `decline_received`, set `doNotContact: true`,
   `relationshipStage: declined`, cancel every open contact task for the person across ALL
   campaigns. Confirm to the user that contact has stopped.
5. Otherwise draft the reply and suggest the next step (meeting, resource, referral ask).

## Completion criteria
Every due follow-up has exactly one prepared task; replies pause sequences; declines stop them.
