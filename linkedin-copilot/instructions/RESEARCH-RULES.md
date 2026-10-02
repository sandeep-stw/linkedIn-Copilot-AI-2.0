# Research rules

1. **Sources, in order of preference:** official company career pages and job listings, company
   websites and press pages, reputable industry publications, public talks/posts the user points to,
   user-provided material. LinkedIn content is used only when the user pastes it or opens it
   themselves; do not scrape LinkedIn.
2. **Every finding is a `research` record** with `question`, `source` (URL or `user_supplied`),
   `observedAt` (date you looked), `facts` (what the source says), `inference` (what you conclude),
   `confidence` (high|medium|low).
3. **Separate fact from inference.** "The listing requires 5+ years of Kubernetes" is a fact;
   "the user is a strong fit" is an inference.
4. **User-stated vs. supported.** Tag claims from the user's own materials as `userStated: true`
   until independently supported or confirmed by the user.
5. **Compensation** only when a source states it. Distinguish base pay from total compensation.
   Never estimate a salary without a source.
6. **Willingness to pay** is never inferred from likes, comments, or generic market reports.
   Prices are hypotheses until someone commits.
7. **Activity:** "active on LinkedIn" requires a dated post/comment the user observed or pasted,
   within `activity_recency_days`. Otherwise `activityStatus: unknown`. A job change is not activity.
8. **Coverage honesty:** never claim exhaustive coverage. State which sources were checked.
9. **Freshness:** research older than `research_stale_days` is flagged stale; refresh before it
   drives a new major recommendation.
10. **Failure:** if a source is unavailable or search tools are missing, keep known evidence, mark
    the gap, lower confidence, and tell the user what is missing. Never fill gaps with invention.
