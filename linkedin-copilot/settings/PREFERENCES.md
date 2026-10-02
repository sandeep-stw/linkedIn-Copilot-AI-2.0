# User Preferences

This file is the single source of truth for settings. Format: `- key: value` under a section.
Edit it directly, or tell Claude in plain words ("give me 20 minutes a day", "turn off post drafting").
Unknown keys or invalid values are reported as issues and never silently enable an external action.

## Goal
- mode: career
- prospect_target: 200
- target_geography: research_and_recommend

## Ownership
- research_before_asking: on
- recommendation_options: 3
- auto_plan: on
- auto_prepare_drafts: on
- auto_prioritize: on
- auto_update_internal_records: on
- auto_adjust_tactics: on
- confirm_major_strategy_changes: on

## Features
- career_research: on
- offer_research: off
- profile_optimization: on
- content_research: on
- post_drafting: on
- prospect_research: on
- relationship_guidance: on
- connection_drafting: on
- follow_up_drafting: on
- validation_interviews: off
- meeting_preparation: on
- weekly_review: on
- reminders: on
- job_search: on
- sales_pitch: on
- nurture: on

## Workload
- minutes_per_day: 15
- max_tasks_per_session: 5
- post_drafts_per_week: 3
- working_days: Monday, Tuesday, Wednesday, Thursday, Friday

## Communication
- language: English
- tone: professional_personal_concise
- verified_claims_only: on
- generic_praise: off
- immediate_pitch: off

## Follow-ups
- first_after_business_days: 5
- second_after_additional_business_days: 7
- max_unanswered: 2
- pause_on_reply: on
- stop_on_decline: on

## Research
- initial_shortlist: 30
- activity_recency_days: 30
- research_stale_days: 30
- validation_participants: 10

## Jobs (career mode — LinkedIn job posts only)
- job_date_posted: past_week
- job_workplace: any
- job_experience: any
- applications_per_week: 5
- min_job_fit: 60
- job_follow_up_business_days: 7

## Sales (business mode)
- deal_follow_up_business_days: 3

## Nurture (business days between useful touches)
- nurture_hot_business_days: 4
- nurture_warm_business_days: 10
- nurture_cold_business_days: 25

## Execution
- linkedin_mode: browser_assisted
- linkedin_open_pages: on
- external_action_approval: on
- background_preparation: on
- daily_prep_time: 08:30
- weekly_review_day: Friday
- weekly_review_time: 17:00
- monthly_review_day: 1
- monthly_review_time: 09:00
- timezone: Asia/Kolkata

## Privacy
- store_credentials: off
- contact_export: off
- retention_days: 180
