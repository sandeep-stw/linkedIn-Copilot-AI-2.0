#!/usr/bin/env python3
"""LinkedIn Copilot storage layer.

The ONLY sanctioned writer of data/*.json and settings/PREFERENCES.md.
Validates records, writes atomically, bumps revisions, keeps backups,
detects concurrent-save conflicts, and renders the dashboard.

Run from anywhere:  python linkedin-copilot/tools/store.py <command> [...]

Commands
  init                         create missing data files
  prefs                        parse + validate PREFERENCES.md, print JSON
  set-pref KEY VALUE           change one preference in place (keeps other Markdown)
  validate                     schema + cross-reference + business-rule check
  get FILE [--id ID] [--where k=v ...]
  next-id FILE                 next free id for FILE
  upsert FILE --file PATH|-  [--expect-revision N] [--actor ai|user]
                               insert or merge record(s) by id
  status [--minutes N]         session-start brief (JSON): what is due, blocked, stale
  followups                    follow-ups due per configured cadence
  apply-features               pause tasks of disabled features; list tasks to reassess
  run start|finish|fail --job NAME [--key KEY] [--note TEXT]
  dashboard                    render dashboard/index.html from current data
  restore FILE --revision N    restore a backup revision (creates a new revision)

Exit codes: 0 ok, 1 usage/error, 2 validation failed, 3 revision conflict, 4 locked/duplicate run.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BACKUPS = DATA / ".backups"
PREFS_PATH = ROOT / "settings" / "PREFERENCES.md"
DASHBOARD = ROOT / "dashboard" / "index.html"
SCHEMA_VERSION = 1
BACKUPS_KEPT = 30

# --------------------------------------------------------------------------- time

FIXED_TZ = {  # fallback when the OS has no IANA tz database (Windows without tzdata)
    "UTC": 0, "Asia/Kolkata": 330, "Asia/Calcutta": 330, "Asia/Dubai": 240, "Asia/Singapore": 480,
    "Asia/Tokyo": 540, "Australia/Brisbane": 600, "Europe/London": 0, "Europe/Berlin": 60,
    "America/New_York": -300, "America/Chicago": -360, "America/Los_Angeles": -480,
}


def get_tz(name):
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name), None
    except Exception:
        if name in FIXED_TZ:
            note = None if FIXED_TZ[name] == 330 or name == "UTC" else \
                f"timezone {name} uses a fixed offset (no DST); install 'tzdata' for exact local time"
            return dt.timezone(dt.timedelta(minutes=FIXED_TZ[name]), name), note
        return dt.timezone.utc, f"unknown timezone '{name}', falling back to UTC"


def now_utc():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(s):
    if not s:
        return None
    try:
        if len(s) == 10:
            return dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc)
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def add_business_days(day, n, working_days):
    wd = {DAY_NAMES.index(d) for d in working_days} or {0, 1, 2, 3, 4}
    while n > 0:
        day += dt.timedelta(days=1)
        if day.weekday() in wd:
            n -= 1
    return day

# --------------------------------------------------------------------------- preferences

ONOFF = ["on", "off"]
FEATURES = ["career_research", "offer_research", "profile_optimization", "content_research", "post_drafting",
            "prospect_research", "relationship_guidance", "connection_drafting", "follow_up_drafting",
            "validation_interviews", "meeting_preparation", "weekly_review", "reminders",
            "job_search", "sales_pitch"]
PREF_SCHEMA = {
    "mode": ["career", "business"],
    "prospect_target": ("int", 1, 5000),
    "target_geography": "str",
    **{k: ONOFF for k in ["research_before_asking", "auto_plan", "auto_prepare_drafts", "auto_prioritize",
                          "auto_update_internal_records", "auto_adjust_tactics", "confirm_major_strategy_changes"]},
    "recommendation_options": ("int", 1, 5),
    **{k: ONOFF for k in FEATURES},
    "minutes_per_day": ("int", 5, 240),
    "max_tasks_per_session": ("int", 1, 20),
    "post_drafts_per_week": ("int", 0, 14),
    "working_days": "days",
    "language": "str",
    "tone": "str",
    **{k: ONOFF for k in ["verified_claims_only", "generic_praise", "immediate_pitch",
                          "pause_on_reply", "stop_on_decline", "external_action_approval",
                          "background_preparation", "store_credentials", "contact_export"]},
    "first_after_business_days": ("int", 1, 30),
    "second_after_additional_business_days": ("int", 1, 30),
    "max_unanswered": ("int", 0, 5),
    # browser_assisted = Claude may open one LinkedIn page per task in a live session; the user acts.
    # Fully automated modes are deliberately not accepted (LinkedIn User Agreement §8.2).
    "linkedin_mode": ["manual_companion", "browser_assisted"],
    "linkedin_open_pages": ONOFF,
    "timezone": "str",
    "daily_prep_time": "hhmm",
    "weekly_review_day": DAY_NAMES,
    "weekly_review_time": "hhmm",
    "monthly_review_day": ("int", 1, 28),
    "monthly_review_time": "hhmm",
    "retention_days": ("int", 7, 3650),
    "activity_recency_days": ("int", 1, 365),
    "research_stale_days": ("int", 1, 365),
    "validation_participants": ("int", 1, 50),
    "initial_shortlist": ("int", 5, 200),
    "job_date_posted": ["past_24h", "past_week", "past_month", "any"],
    "job_workplace": ["any", "remote", "hybrid", "onsite"],
    "job_experience": ["any", "internship", "entry", "associate", "mid_senior", "director", "executive"],
    "applications_per_week": ("int", 0, 50),
    "min_job_fit": ("int", 0, 100),
    "job_follow_up_business_days": ("int", 1, 30),
    "deal_follow_up_business_days": ("int", 1, 30),
}
# Safety-critical values that must never be silently enabled by a typo or unknown value.
SAFE_DEFAULTS = {"store_credentials": "off", "contact_export": "off", "external_action_approval": "on",
                 "background_preparation": "off", "verified_claims_only": "on"}
PREF_LINE = re.compile(r"^(\s*-\s*)([A-Za-z0-9_]+)(\s*:\s*)(.*?)\s*$")


def load_prefs():
    issues, values, seen = [], {}, set()
    if not PREFS_PATH.exists():
        return {}, [f"missing {PREFS_PATH}"]
    for n, line in enumerate(PREFS_PATH.read_text(encoding="utf-8").splitlines(), 1):
        m = PREF_LINE.match(line)
        if not m:
            continue
        key, raw = m.group(2), m.group(4)
        if key in seen:
            issues.append(f"line {n}: duplicate key '{key}' (first value kept)")
            continue
        seen.add(key)
        rule = PREF_SCHEMA.get(key)
        if rule is None:
            issues.append(f"line {n}: unknown key '{key}' ignored")
            continue
        val, err = coerce(raw, rule)
        if err:
            issues.append(f"line {n}: {key}: {err}")
            if key in SAFE_DEFAULTS:
                values[key] = SAFE_DEFAULTS[key]
            continue
        values[key] = val
    for key in PREF_SCHEMA:
        if key not in values and key not in SAFE_DEFAULTS:
            if key in FEATURES:
                values[key] = "off"
                issues.append(f"missing feature '{key}' treated as off")
    for key, safe in SAFE_DEFAULTS.items():
        values.setdefault(key, safe)
    values.setdefault("timezone", "UTC")
    values.setdefault("working_days", DAY_NAMES[:5])
    return values, issues


def coerce(raw, rule):
    raw = raw.strip()
    if isinstance(rule, list):
        return (raw, None) if raw in rule else (None, f"'{raw}' not one of {rule}")
    if isinstance(rule, tuple):
        try:
            v = int(raw)
        except ValueError:
            return None, f"'{raw}' is not an integer"
        return (v, None) if rule[1] <= v <= rule[2] else (None, f"{v} outside {rule[1]}..{rule[2]}")
    if rule == "days":
        days = [d.strip() for d in raw.split(",") if d.strip()]
        bad = [d for d in days if d not in DAY_NAMES]
        return (days, None) if days and not bad else (None, f"invalid day(s) {bad or raw}")
    if rule == "hhmm":
        return (raw, None) if re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", raw) else (None, f"'{raw}' is not HH:MM")
    return (raw, None) if raw else (None, "empty value")


def set_pref(key, value):
    if key not in PREF_SCHEMA:
        die(f"unknown preference '{key}'", 2)
    val, err = coerce(value, PREF_SCHEMA[key])
    if err:
        die(f"{key}: {err}", 2)
    text = PREFS_PATH.read_text(encoding="utf-8")
    lines, found = text.splitlines(keepends=True), False
    for i, line in enumerate(lines):
        m = PREF_LINE.match(line.rstrip("\r\n"))
        if m and m.group(2) == key:
            eol = line[len(line.rstrip("\r\n")):]
            lines[i] = f"{m.group(1)}{key}{m.group(3)}{value}{eol}"
            found = True
            break
    if not found:
        die(f"'{key}' not present in PREFERENCES.md; add it under the right section first", 2)
    backup_file(PREFS_PATH, "PREFERENCES", int(time.time()))
    atomic_write(PREFS_PATH, "".join(lines))
    return val

# --------------------------------------------------------------------------- schemas

TASK_STATES = ["pending", "prepared", "awaiting_user", "completed", "skipped", "paused", "blocked", "cancelled"]
OPEN_TASK_STATES = ["pending", "prepared", "awaiting_user", "blocked"]
ACTION_STATES = ["drafted", "approved", "completed", "rejected"]
CONTACT_TASK_TYPES = ["connection_note", "message", "follow_up", "comment", "meeting_invite",
                      "referral_request", "resource_share", "interview_invite",
                      "job_follow_up", "pitch", "sales_follow_up", "send_proposal"]
JOB_STAGES = ["found", "shortlisted", "preparing", "applied", "screening", "interviewing", "offer",
              "accepted", "rejected", "withdrawn", "closed"]
JOB_APPLIED_STAGES = ["applied", "screening", "interviewing", "offer", "accepted", "rejected"]
DEAL_STAGES = ["conversation", "discovery", "proposal_drafted", "proposal_sent", "negotiation", "won", "lost", "paused"]
CONTENT_KINDS = ["post", "pitch_kit", "one_pager", "proposal", "cover_note", "resume_tailoring",
                 "objection_answers", "interview_prep"]
SCHEMAS = {
    "research": {"req": ["question", "observedAt", "confidence", "source"],
                 "enum": {"confidence": ["high", "medium", "low"]}, "campaign": False},
    "recommendations": {"req": ["option", "rank", "evidenceRefs", "selectionState", "researchVersion"],
                        "enum": {"selectionState": ["proposed", "selected", "rejected", "superseded"]},
                        "campaign": False, "refs": {"evidenceRefs": "research"}},
    "campaign": {"req": ["mode", "goal", "stage", "status", "selectedRecommendationId"],
                 "enum": {"mode": ["career", "business"], "status": ["active", "paused", "archived"]},
                 "campaign": False, "refs": {"selectedRecommendationId": "recommendations"}},
    "prospects": {"req": ["name", "category", "source", "fitReason", "relationshipStage", "doNotContact",
                          "activityStatus"],
                  "enum": {"relationshipStage": ["shortlisted", "engaging", "invited", "connected", "conversing",
                                                 "meeting", "referral", "opportunity", "paused", "declined"],
                           "activityStatus": ["active", "inactive", "unknown"]},
                  "refs": {"nextActionId": "tasks"}},
    "interactions": {"req": ["prospectId", "type", "status", "direction"],
                     "enum": {"status": ACTION_STATES, "direction": ["outgoing", "incoming"],
                              "type": CONTACT_TASK_TYPES + ["reply_received", "decline_received", "meeting_note"]},
                     "refs": {"prospectId": "prospects", "taskId": "tasks"}},
    "tasks": {"req": ["type", "feature", "priority", "status", "title", "estMinutes", "dedupeKey"],
              "enum": {"status": TASK_STATES, "feature": FEATURES + ["core"]},
              "refs": {"relatedIds": "*"}},
    "content": {"req": ["audience", "objective", "status", "body"],
                "enum": {"status": ["idea"] + ACTION_STATES, "kind": CONTENT_KINDS},
                "refs": {"jobId": "jobs", "dealId": "deals"}},
    "jobs": {"req": ["title", "company", "source", "stage", "fitScore", "fitReason"],
             "enum": {"stage": JOB_STAGES, "source": ["linkedin_job_post"],
                      "workplace": ["remote", "hybrid", "onsite", "unknown"]},
             "refs": {"referralProspectIds": "prospects", "coverNoteId": "content", "nextActionId": "tasks"}},
    "deals": {"req": ["prospectId", "offer", "stage", "nextStep"],
              "enum": {"stage": DEAL_STAGES},
              "refs": {"prospectId": "prospects", "proposalId": "content", "nextActionId": "tasks"}},
    "interviews": {"req": ["prospectId", "schedulingState", "notesProvenance"],
                   "enum": {"schedulingState": ["proposed", "invited", "scheduled", "completed", "declined",
                                                "no_response"],
                            "notesProvenance": ["none", "user_notes", "ai_summary_unconfirmed", "ai_summary_confirmed"]},
                   "refs": {"prospectId": "prospects"}},
    "opportunities": {"req": ["type", "stage", "outcome"],
                      "enum": {"type": ["referral", "application", "interview", "offer", "pilot", "proposal", "sale",
                                        "advice_call"],
                               "outcome": ["open", "won", "lost", "withdrawn"]},
                      "refs": {"prospectId": "prospects"}},
    "metrics": {"req": ["period", "name", "source", "calculation"],
                "enum": {"source": ["user_entered", "integration_confirmed", "computed", "unknown"]}},
    "decisions": {"req": ["change", "owner", "reason", "decidedAt"],
                  "enum": {"owner": ["user", "ai"]}, "campaign": False},
    "runs": {"req": ["job", "runKey", "status", "startedAt"],
             "enum": {"status": ["running", "succeeded", "failed", "skipped"]}, "campaign": False},
}
FILES = list(SCHEMAS)
ID_PREFIX = {"research": "r", "recommendations": "rec", "campaign": "c", "prospects": "p", "interactions": "i",
             "tasks": "t", "content": "post", "interviews": "iv", "opportunities": "o", "metrics": "m",
             "decisions": "d", "runs": "run", "jobs": "job", "deals": "deal"}
LINKEDIN_JOB_ID = re.compile(r"linkedin\.com/jobs/(?:view/(?:[^/?#]*-)?(\d+)|.*[?&]currentJobId=(\d+))")


def linkedin_job_id(url):
    m = LINKEDIN_JOB_ID.search(url or "")
    return (m.group(1) or m.group(2)) if m else None


def path_of(name):
    if name not in SCHEMAS:
        die(f"unknown data file '{name}'. Known: {', '.join(FILES)}")
    return DATA / f"{name}.json"


def empty_doc():
    return {"schemaVersion": SCHEMA_VERSION, "revision": 0, "updatedAt": iso(now_utc()), "records": []}


def load(name):
    p = path_of(name)
    if not p.exists():
        return empty_doc()
    doc = json.loads(p.read_text(encoding="utf-8"))
    if doc.get("schemaVersion") != SCHEMA_VERSION:
        die(f"{name}.json schemaVersion {doc.get('schemaVersion')} != {SCHEMA_VERSION}; migrate first", 2)
    return doc


def load_all():
    return {n: load(n) for n in FILES}


def record_errors(name, rec, all_docs, prefs):
    s, errs = SCHEMAS[name], []
    for f in ["id", "createdAt", "updatedAt", "provenance"] + s["req"]:
        if rec.get(f) in (None, ""):
            errs.append(f"missing '{f}'")
    if s.get("campaign", True) and not rec.get("campaignId"):
        errs.append("missing 'campaignId'")
    for f, allowed in s.get("enum", {}).items():
        if f in rec and rec[f] is not None and rec[f] not in allowed:
            errs.append(f"{f}='{rec[f]}' not in {allowed}")
    ids = {n: {r["id"] for r in d["records"]} for n, d in all_docs.items()}
    every = set().union(*ids.values())
    if rec.get("campaignId") and rec["campaignId"] not in ids["campaign"]:
        errs.append(f"campaignId '{rec['campaignId']}' not found")
    for f, target in s.get("refs", {}).items():
        vals = rec.get(f)
        for v in (vals if isinstance(vals, list) else [vals]):
            if v and v not in (every if target == "*" else ids[target]):
                errs.append(f"{f} -> '{v}' not found in {target}")
    # business rules
    if name == "interactions" and rec.get("status") == "completed" and rec.get("direction") == "outgoing" \
            and rec.get("confirmationSource") not in ("user_confirmed", "integration_confirmed"):
        errs.append("completed outgoing interaction needs confirmationSource user_confirmed|integration_confirmed")
    if name == "interactions" and rec.get("direction") == "incoming" and rec.get("status") != "completed":
        errs.append("incoming interactions record something that happened: status must be completed")
    if name == "tasks" and rec.get("status") == "completed" and not rec.get("completionEvidence"):
        errs.append("completed task needs completionEvidence")
    if name == "content" and rec.get("kind", "post") == "post" and not rec.get("hook"):
        errs.append("post content needs a 'hook'")
    if name == "content" and rec.get("kind", "post") == "post" and rec.get("status") == "completed" \
            and not rec.get("publicationEvidence"):
        errs.append("published content needs publicationEvidence (post URL or 'user_confirmed')")
    if name == "jobs":
        if rec.get("postingUrl") and not linkedin_job_id(rec["postingUrl"]):
            errs.append("postingUrl must be a LinkedIn job post URL (linkedin.com/jobs/view/<id>)")
        if not isinstance(rec.get("fitScore"), int) or not 0 <= rec["fitScore"] <= 100:
            errs.append("fitScore must be an integer 0-100")
        if rec.get("stage") in JOB_APPLIED_STAGES and (not rec.get("appliedAt") or rec.get("confirmationSource")
                                                       not in ("user_confirmed", "integration_confirmed")):
            errs.append("applied (or later) needs appliedAt + confirmationSource user_confirmed — "
                        "only the student's confirmation moves a job to applied")
    if name == "deals":
        if rec.get("stage") in ("proposal_sent", "negotiation", "won") and rec.get("confirmationSource") \
                not in ("user_confirmed", "integration_confirmed"):
            errs.append(f"deal stage '{rec.get('stage')}' needs confirmationSource user_confirmed")
        if rec.get("stage") == "won" and not rec.get("outcomeEvidence"):
            errs.append("won deal needs outcomeEvidence (what the buyer committed to, in the user's words)")
        if rec.get("stage") not in ("won", "lost", "paused") and not rec.get("nextStepDue"):
            errs.append("open deal needs nextStepDue (YYYY-MM-DD)")
    if name == "prospects" and rec.get("activityStatus") == "active":
        ev = rec.get("activityEvidence") or {}
        seen = parse_time(ev.get("observedAt")) if isinstance(ev, dict) else None
        if not seen or not ev.get("description"):
            errs.append("activityStatus 'active' needs activityEvidence {observedAt, description, url?}")
        elif (now_utc() - seen).days > prefs.get("activity_recency_days", 30):
            errs.append("activity evidence older than activity_recency_days; use 'unknown' or 'inactive'")
    if name == "tasks" and rec.get("type") in CONTACT_TASK_TYPES and rec.get("status") in OPEN_TASK_STATES:
        dnc = {p["id"] for p in all_docs["prospects"]["records"] if p.get("doNotContact")}
        hit = [x for x in rec.get("relatedIds", []) if x in dnc]
        if hit:
            errs.append(f"contact task targets do-not-contact prospect(s) {hit}")
    if name == "tasks" and rec.get("status") in OPEN_TASK_STATES and prefs.get(rec.get("feature")) == "off":
        errs.append(f"feature '{rec.get('feature')}' is off; new/open tasks not allowed (use status paused)")
    if name == "metrics" and rec.get("source") == "unknown" and rec.get("numerator") not in (None,):
        errs.append("unknown metrics must have numerator null, never 0")
    return errs


def validate_all(docs, prefs):
    problems = []
    for name, doc in docs.items():
        seen = set()
        for r in doc["records"]:
            if r.get("id") in seen:
                problems.append(f"{name}: duplicate id {r.get('id')}")
            seen.add(r.get("id"))
            for e in record_errors(name, r, docs, prefs):
                # feature-off is a state issue for existing tasks, surfaced by apply-features instead
                if "feature '" in e:
                    continue
                problems.append(f"{name}/{r.get('id')}: {e}")
    keys = {}
    for t in docs["tasks"]["records"]:
        if t.get("status") in OPEN_TASK_STATES + ["paused"]:
            if t["dedupeKey"] in keys:
                problems.append(f"tasks: duplicate open dedupeKey '{t['dedupeKey']}' ({keys[t['dedupeKey']]}, {t['id']})")
            keys[t.get("dedupeKey")] = t["id"]
    active = [c for c in docs["campaign"]["records"] if c.get("status") == "active"]
    if len(active) > 1:
        problems.append(f"campaign: more than one active campaign {[c['id'] for c in active]}")
    return problems

# --------------------------------------------------------------------------- io


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def backup_file(path, stem, rev):
    if not path.exists():
        return
    BACKUPS.mkdir(parents=True, exist_ok=True)
    (BACKUPS / f"{stem}.r{rev}{path.suffix}").write_bytes(path.read_bytes())
    olds = sorted(BACKUPS.glob(f"{stem}.r*{path.suffix}"), key=lambda p: p.stat().st_mtime)
    for p in olds[:-BACKUPS_KEPT]:
        p.unlink()


class Lock:
    def __init__(self):
        self.path = DATA / ".lock"

    def __enter__(self):
        DATA.mkdir(parents=True, exist_ok=True)
        for _ in range(50):
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                if time.time() - self.path.stat().st_mtime > 60:
                    self.path.unlink(missing_ok=True)  # stale lock from a crashed writer
                    continue
                time.sleep(0.1)
        die("data store is locked by another writer", 4)

    def __exit__(self, *a):
        os.close(self.fd)
        self.path.unlink(missing_ok=True)


def save(name, doc, expect_revision=None):
    current = load(name)
    if expect_revision is not None and current["revision"] != expect_revision:
        die(f"CONFLICT: {name}.json is at revision {current['revision']}, expected {expect_revision}. "
            f"Re-read, merge, and retry.", 3)
    backup_file(path_of(name), name, current["revision"])
    doc["revision"] = current["revision"] + 1
    doc["updatedAt"] = iso(now_utc())
    atomic_write(path_of(name), json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return doc["revision"]


def next_id(name, doc):
    pre = ID_PREFIX[name] + "_"
    nums = [int(r["id"][len(pre):]) for r in doc["records"] if str(r.get("id", "")).startswith(pre)
            and r["id"][len(pre):].isdigit()]
    return f"{pre}{(max(nums) + 1 if nums else 1):04d}"


def upsert(name, payload, expect_revision, actor):
    prefs, _ = load_prefs()
    with Lock():
        docs = load_all()
        doc = docs[name]
        incoming = payload if isinstance(payload, list) else [payload]
        stamp, changed = iso(now_utc()), []
        for rec in incoming:
            if not isinstance(rec, dict):
                die("each record must be a JSON object")
            rec = dict(rec)
            if not rec.get("id"):
                rec["id"] = next_id(name, doc)
            existing = next((r for r in doc["records"] if r["id"] == rec["id"]), None)
            if existing:
                if name == "prospects" and existing.get("doNotContact") and rec.get("doNotContact") is False \
                        and actor != "user":
                    die(f"{rec['id']}: only the user may clear a do-not-contact flag", 2)
                merged = {**existing, **rec, "createdAt": existing.get("createdAt", stamp), "updatedAt": stamp}
            else:
                merged = {**rec, "createdAt": rec.get("createdAt", stamp), "updatedAt": stamp}
                merged.setdefault("provenance", actor)
            if name == "tasks" and not existing:
                dup = next((t for t in doc["records"] if t.get("dedupeKey") == merged.get("dedupeKey")
                            and t["status"] in OPEN_TASK_STATES + ["paused"]), None)
                if dup:
                    print(json.dumps({"skipped_duplicate": merged.get("dedupeKey"), "existingId": dup["id"]}))
                    continue
            if name == "jobs" and not existing and linkedin_job_id(merged.get("postingUrl")):
                jid = linkedin_job_id(merged["postingUrl"])
                dup = next((j for j in doc["records"] if linkedin_job_id(j.get("postingUrl")) == jid), None)
                if dup:  # the same LinkedIn post pasted twice
                    print(json.dumps({"skipped_duplicate": f"linkedin_job:{jid}", "existingId": dup["id"]}))
                    continue
            doc["records"] = [r for r in doc["records"] if r["id"] != merged["id"]] + [merged]
            errs = record_errors(name, merged, docs, prefs)
            if errs:
                die(f"VALIDATION FAILED {name}/{merged['id']}:\n  - " + "\n  - ".join(errs), 2)
            changed.append(merged["id"])
        if not changed:
            print(json.dumps({"ok": True, "changed": []}))
            return
        rev = save(name, doc, expect_revision)
        cancelled = []
        if name == "prospects":  # a decline/opt-out stops every open contact task, across campaigns
            dnc = {r["id"] for r in doc["records"] if r["id"] in changed and r.get("doNotContact")}
            tasks = docs["tasks"]
            for t in tasks["records"]:
                if t["type"] in CONTACT_TASK_TYPES and t["status"] in OPEN_TASK_STATES + ["paused"] \
                        and dnc.intersection(t.get("relatedIds", [])):
                    t.update(status="cancelled", cancelledReason="do_not_contact", updatedAt=stamp)
                    cancelled.append(t["id"])
            if cancelled:
                save("tasks", tasks)
    print(json.dumps({"ok": True, "file": name, "revision": rev, "changed": changed,
                      **({"cancelledTasks": cancelled} if cancelled else {})}))

# --------------------------------------------------------------------------- analysis


def today_local(prefs):
    tz, note = get_tz(prefs.get("timezone", "UTC"))
    return dt.datetime.now(tz), note


def compute_followups(docs, prefs):
    if prefs.get("follow_up_drafting") == "off":
        return []
    now, _ = today_local(prefs)
    wd = prefs.get("working_days", DAY_NAMES[:5])
    first = prefs.get("first_after_business_days", 5)
    second = prefs.get("second_after_additional_business_days", 7)
    max_un = prefs.get("max_unanswered", 2)
    by_p = {}
    for i in docs["interactions"]["records"]:
        by_p.setdefault(i["prospectId"], []).append(i)
    out = []
    for p in docs["prospects"]["records"]:
        if p.get("doNotContact") or p.get("relationshipStage") in ("declined", "paused"):
            continue
        hist = sorted([i for i in by_p.get(p["id"], []) if i["status"] == "completed"],
                      key=lambda i: i.get("occurredAt") or i["updatedAt"])
        if not hist:
            continue
        last_in = max((parse_time(i.get("occurredAt") or i["updatedAt"]) for i in hist
                       if i["direction"] == "incoming"), default=None)
        outs = [i for i in hist if i["direction"] == "outgoing" and
                (last_in is None or parse_time(i.get("occurredAt") or i["updatedAt"]) > last_in)]
        if any(i["type"] == "decline_received" for i in hist):
            continue
        if last_in and not outs:
            out.append({"prospectId": p["id"], "name": p["name"], "action": "reassess_reply",
                        "reason": "reply received; sequence paused for reassessment"})
            continue
        if not outs:
            continue
        unanswered_fups = sum(1 for i in outs if i["type"] == "follow_up")
        if unanswered_fups >= max_un:
            out.append({"prospectId": p["id"], "name": p["name"], "action": "pause",
                        "reason": f"{unanswered_fups} unanswered follow-ups; pause per max_unanswered={max_un}"})
            continue
        last = parse_time(outs[-1].get("occurredAt") or outs[-1]["updatedAt"]).astimezone(now.tzinfo).date()
        due = add_business_days(last, first if unanswered_fups == 0 else second, wd)
        if p.get("recipientTimingNote"):
            out.append({"prospectId": p["id"], "name": p["name"], "action": "respect_recipient_timing",
                        "reason": p["recipientTimingNote"], "cadenceDue": due.isoformat()})
        elif due <= now.date():
            out.append({"prospectId": p["id"], "name": p["name"], "action": f"follow_up_{unanswered_fups + 1}",
                        "due": due.isoformat(), "lastOutgoing": last.isoformat()})
    return out


JOB_URL_CODES = {
    "f_TPR": ("job_date_posted", {"past_24h": "r86400", "past_week": "r604800", "past_month": "r2592000"}),
    "f_WT": ("job_workplace", {"onsite": "1", "remote": "2", "hybrid": "3"}),
    "f_E": ("job_experience", {"internship": "1", "entry": "2", "associate": "3", "mid_senior": "4",
                               "director": "5", "executive": "6"}),
}


def linkedin_jobs_url(keywords, location, prefs):
    """A LinkedIn Jobs search link the STUDENT opens; Claude never loads or reads the results page."""
    from urllib.parse import urlencode
    q = {"keywords": keywords}
    if location:
        q["location"] = location
    for param, (key, codes) in JOB_URL_CODES.items():
        code = codes.get(prefs.get(key, "any"))
        if code:
            q[param] = code
    q["sortBy"] = "DD"
    return "https://www.linkedin.com/jobs/search/?" + urlencode(q)


def compute_pipeline(docs, prefs, today):
    wd = prefs.get("working_days", DAY_NAMES[:5])
    tz, _ = get_tz(prefs.get("timezone", "UTC"))
    n_job = prefs.get("job_follow_up_business_days", 7)
    job_fu = []
    for j in docs["jobs"]["records"]:
        applied = parse_time(j.get("appliedAt"))
        if j["stage"] == "applied" and applied and not j.get("lastFollowUpAt"):
            due = add_business_days(applied.astimezone(tz).date(), n_job, wd)
            if due <= today:
                job_fu.append({"jobId": j["id"], "title": j["title"], "company": j["company"], "due": due.isoformat()})
    deals_due = [{"dealId": d["id"], "prospectId": d["prospectId"], "stage": d["stage"], "nextStep": d["nextStep"],
                  "due": d.get("nextStepDue")} for d in docs["deals"]["records"]
                 if d["stage"] not in ("won", "lost", "paused") and d.get("nextStepDue")
                 and dt.date.fromisoformat(d["nextStepDue"][:10]) <= today]
    week_start = today - dt.timedelta(days=today.weekday())
    applied_week = sum(1 for j in docs["jobs"]["records"] if parse_time(j.get("appliedAt"))
                       and parse_time(j["appliedAt"]).astimezone(tz).date() >= week_start)
    count = lambda recs, f: {s: sum(1 for r in recs if r["stage"] == s) for s in f if any(r["stage"] == s for r in recs)}
    return {"jobFollowups": job_fu, "dealsDue": deals_due,
            "jobPipeline": count(docs["jobs"]["records"], JOB_STAGES),
            "dealPipeline": count(docs["deals"]["records"], DEAL_STAGES),
            "applicationsThisWeek": applied_week, "applicationsTarget": prefs.get("applications_per_week")}


def compute_status(minutes=None):
    prefs, pref_issues = load_prefs()
    docs = load_all()
    now, tz_note = today_local(prefs)
    today = now.date()
    tasks = docs["tasks"]["records"]
    open_tasks = [t for t in tasks if t["status"] in OPEN_TASK_STATES]

    def due(t):
        d = t.get("dueDate")
        return dt.date.fromisoformat(d[:10]) if d else today

    budget = minutes if minutes is not None else prefs.get("minutes_per_day", 15)
    max_tasks = prefs.get("max_tasks_per_session", 5)
    ready = sorted([t for t in open_tasks if t["status"] != "blocked" and due(t) <= today
                    and prefs.get(t["feature"], "on") != "off"],
                   key=lambda t: (t["priority"], due(t), t["estMinutes"]))
    plan, used = [], 0
    for t in ready:
        if len(plan) >= max_tasks:
            break
        if used + t["estMinutes"] <= budget:
            plan.append(t)
            used += t["estMinutes"]
    if not plan and ready:  # tiny budget: still offer the single highest-value feasible action
        smallest = min(ready, key=lambda t: (t["estMinutes"], t["priority"]))
        plan, used = [smallest], smallest["estMinutes"]
    stale_days = prefs.get("research_stale_days", 30)
    stale = [r["id"] for r in docs["research"]["records"]
             if (parse_time(r["observedAt"]) and (now_utc() - parse_time(r["observedAt"])).days > stale_days)]
    active = next((c for c in docs["campaign"]["records"] if c.get("status") == "active"), None)
    proposed = [r for r in docs["recommendations"]["records"] if r["selectionState"] == "proposed"]
    runs = sorted(docs["runs"]["records"], key=lambda r: r["startedAt"])
    last_ok = next((r for r in reversed(runs) if r["status"] == "succeeded"), None)
    failures = [r for r in runs[-10:] if r["status"] == "failed"]
    paused_by_feature = [t["id"] for t in tasks if t["status"] in OPEN_TASK_STATES and prefs.get(t["feature"]) == "off"]
    reassess = [t["id"] for t in tasks if t["status"] == "paused" and t.get("pausedReason", "").startswith("feature_off")
                and prefs.get(t["feature"]) == "on"]
    if not active:
        stage = "onboarding_selection" if proposed else "onboarding_research"
    else:
        stage = active.get("stage")
    nxt = None
    if not active and proposed:
        nxt = "Review the ranked options and select a primary direction."
    elif not active:
        nxt = "Run /linkedin-copilot and share your Upwork profile, résumé PDF and/or LinkedIn profile."
    elif plan:
        nxt = f"{plan[0]['title']} (~{plan[0]['estMinutes']} min)"
    else:
        nxt = "No tasks due. Run the daily session to prepare the next actions."
    return {
        "generatedAt": iso(now_utc()), "localTime": now.strftime("%Y-%m-%d %H:%M %Z"),
        "isWorkingDay": DAY_NAMES[today.weekday()] in prefs.get("working_days", DAY_NAMES[:5]),
        "stage": stage, "activeCampaign": active and {k: active.get(k) for k in ("id", "mode", "goal", "stage")},
        "nextAction": nxt,
        "todayPlan": [{k: t.get(k) for k in ("id", "title", "type", "priority", "estMinutes", "status", "dueDate")}
                      for t in plan],
        "planMinutes": used, "budgetMinutes": budget,
        "overdue": [t["id"] for t in open_tasks if due(t) < today],
        "awaitingUser": [t["id"] for t in open_tasks if t["status"] == "awaiting_user"],
        "blocked": [{"id": t["id"], "reason": t.get("blockedReason")} for t in open_tasks if t["status"] == "blocked"],
        "pendingDecisions": [r["id"] for r in proposed],
        "followups": compute_followups(docs, prefs),
        **compute_pipeline(docs, prefs, today),
        "staleResearch": stale,
        "tasksNeedingFeaturePause": paused_by_feature,
        "pausedTasksToReassess": reassess,
        "lastSuccessfulRun": last_ok and {k: last_ok[k] for k in ("job", "runKey", "finishedAt") if k in last_ok},
        "recentFailures": [{k: r.get(k) for k in ("job", "runKey", "note")} for r in failures],
        "preferenceIssues": pref_issues + ([tz_note] if tz_note else []),
        "dataProblems": validate_all(docs, prefs),
        "backgroundPreparation": prefs.get("background_preparation"),
    }


def apply_features():
    prefs, _ = load_prefs()
    with Lock():
        doc = load("tasks")
        stamp, paused = iso(now_utc()), []
        for t in doc["records"]:
            if t["status"] in OPEN_TASK_STATES and prefs.get(t["feature"]) == "off":
                t.update(status="paused", pausedReason=f"feature_off:{t['feature']}", previousStatus=t["status"],
                         updatedAt=stamp)
                paused.append(t["id"])
        reassess = [t["id"] for t in doc["records"] if t["status"] == "paused"
                    and t.get("pausedReason", "").startswith("feature_off") and prefs.get(t["feature"]) == "on"]
        rev = save("tasks", doc) if paused else doc["revision"]
    print(json.dumps({"paused": paused, "reassessBeforeResuming": reassess, "revision": rev}))


def period_key(now, period):
    if period == "week":
        y, w, _ = now.isocalendar()
        return f"{y}-W{w:02d}"
    return now.strftime("%Y-%m" if period == "month" else "%Y-%m-%d")


def run_cmd(action, job, key, note, period="day"):
    prefs, _ = load_prefs()
    now, _ = today_local(prefs)
    key = key or period_key(now, period)
    with Lock():
        doc = load("runs")
        cur = next((r for r in doc["records"] if r["job"] == job and r["runKey"] == key), None)
        stamp = iso(now_utc())
        if action == "start":
            if cur and cur["status"] in ("succeeded", "skipped"):
                die(f"DUPLICATE: {job} already {cur['status']} for {key}", 4)
            if cur and cur["status"] == "running" and (now_utc() - parse_time(cur["startedAt"])).seconds < 3600:
                die(f"DUPLICATE: {job} for {key} is already running since {cur['startedAt']}", 4)
            rec = cur or {"id": next_id("runs", doc), "job": job, "runKey": key, "createdAt": stamp,
                          "provenance": "scheduler"}
            rec.update(status="running", startedAt=stamp, updatedAt=stamp, note=note,
                       attempts=rec.get("attempts", 0) + 1)
        else:
            if not cur:
                die(f"no run {job}/{key} to {action}")
            rec = cur
            rec.update(status={"finish": "succeeded", "fail": "failed", "skip": "skipped"}[action],
                       finishedAt=stamp, updatedAt=stamp, note=note or rec.get("note"))
        doc["records"] = [r for r in doc["records"] if r["id"] != rec["id"]] + [rec]
        doc["records"] = doc["records"][-200:]
        save("runs", doc)
    print(json.dumps({"ok": True, "run": rec}))

# --------------------------------------------------------------------------- dashboard


def e(v):
    if v is None or v == "":
        return '<span class="unk">unknown</span>'
    if isinstance(v, (list, dict)):
        v = json.dumps(v, ensure_ascii=False)
    return html.escape(str(v))


def table(rows, cols, empty="Nothing recorded yet."):
    if not rows:
        return f'<p class="muted">{empty}</p>'
    head = "".join(f"<th>{html.escape(c[0])}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{c[1](r)}</td>" for c in cols) + "</tr>" for r in rows)
    return f'<div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def draft_box(text, label="Copy draft"):
    if not text:
        return ""
    return (f'<div class="draft"><pre>{html.escape(text)}</pre>'
            f'<button class="copy" type="button">{label}</button></div>')


def render_dashboard():
    prefs, pref_issues = load_prefs()
    docs = load_all()
    st = compute_status()
    R = {n: d["records"] for n, d in docs.items()}
    by_id = {r["id"]: r for recs in R.values() for r in recs}
    pros = {p["id"]: p for p in R["prospects"]}

    def pname(pid):
        return e(pros.get(pid, {}).get("name", pid))

    today_cards = ""
    for t in st["todayPlan"]:
        full = by_id[t["id"]]
        draft = full.get("draft") or (by_id.get(full.get("draftRef"), {}) or {}).get("body")
        link = full.get("linkedinUrl") or "https://www.linkedin.com/"
        today_cards += f"""<article class="card"><header><span class="pill p{e(full['priority'])}">P{e(full['priority'])}</span>
<h3>{e(full['title'])}</h3><span class="muted">~{e(full['estMinutes'])} min · {e(full['status'])}</span></header>
<p><b>Why:</b> {e(full.get('reason'))}</p>{draft_box(draft)}
<div class="row"><a class="btn" href="{html.escape(link) if link.startswith('https://') else 'https://www.linkedin.com/'}" target="_blank" rel="noopener noreferrer">Open LinkedIn</a>
<span class="hint">Done? Tell Claude: <code>done {e(full['id'])}</code> · Skip: <code>skip {e(full['id'])}</code></span></div></article>"""
    if not today_cards:
        today_cards = f'<p class="muted">{e(st["nextAction"])}</p>'

    camp = st["activeCampaign"] or {}
    goal = next((c for c in R["campaign"] if c.get("status") == "active"), {})
    funnel_metrics = [m for m in R["metrics"]]

    sections = {
        "Today": f"""<div class="next"><span>Next action</span><strong>{e(st['nextAction'])}</strong></div>
{today_cards}
<h3>Follow-ups</h3>{table(st['followups'], [('Prospect', lambda r: e(r['name'])), ('Action', lambda r: e(r['action'])), ('Due / reason', lambda r: e(r.get('due') or r.get('reason')))], 'No follow-ups due.')}
<h3>Applications to follow up</h3>{table(st['jobFollowups'], [('Role', lambda r: e(r['title'])), ('Company', lambda r: e(r['company'])), ('Due', lambda r: e(r['due']))], 'None due.')}
<h3>Deal next steps due</h3>{table(st['dealsDue'], [('Buyer', lambda r: pname(r['prospectId'])), ('Stage', lambda r: e(r['stage'])), ('Next step', lambda r: e(r['nextStep'])), ('Due', lambda r: e(r['due']))], 'None due.')}""",
        "Recommendations": table(sorted(R["recommendations"], key=lambda r: (r.get("researchVersion", ""), r["rank"])),
            [("Rank", lambda r: e(r["rank"])), ("Option", lambda r: e(r["option"])), ("Fit", lambda r: e(r.get("fit"))),
             ("Gaps", lambda r: e(r.get("gaps"))), ("Confidence", lambda r: e(r.get("confidence"))),
             ("Evidence", lambda r: e(", ".join(r.get("evidenceRefs", [])))), ("State", lambda r: e(r["selectionState"]))],
            "No research yet. Run onboarding: /linkedin-copilot onboard"),
        "Goal": f"""<dl class="kv"><dt>Mode</dt><dd>{e(goal.get('mode'))}</dd><dt>Goal</dt><dd>{e(goal.get('goal'))}</dd>
<dt>Stage</dt><dd>{e(goal.get('stage'))}</dd><dt>Success measures</dt><dd>{e(goal.get('successMeasures'))}</dd>
<dt>Milestones</dt><dd>{e(goal.get('milestones'))}</dd><dt>Evidence gaps</dt><dd>{e(goal.get('evidenceGaps'))}</dd>
<dt>Blockers</dt><dd>{e(goal.get('blockers'))}</dd></dl>""",
        "Prospects": table(R["prospects"], [("Name", lambda r: e(r["name"])), ("Role", lambda r: e(r.get("role"))),
            ("Company", lambda r: e(r.get("company"))), ("Category", lambda r: e(r["category"])),
            ("Fit", lambda r: e(r.get("fitScore"))), ("Activity", lambda r: e(r["activityStatus"])),
            ("Stage", lambda r: e(r["relationshipStage"])),
            ("DNC", lambda r: "⛔" if r.get("doNotContact") else ""), ("Next", lambda r: e(r.get("nextActionId")))]),
        "Conversations": table(sorted(R["interactions"], key=lambda r: r.get("occurredAt") or r["updatedAt"], reverse=True),
            [("When", lambda r: e(r.get("occurredAt"))), ("Prospect", lambda r: pname(r["prospectId"])),
             ("Type", lambda r: e(r["type"])), ("Dir", lambda r: e(r["direction"])), ("Status", lambda r: e(r["status"])),
             ("Content", lambda r: draft_box(r.get("content"), "Copy") if r["status"] in ("drafted", "approved") else e(r.get("content"))),
             ("Confirmed by", lambda r: e(r.get("confirmationSource")))]),
        "Content": table(R["content"], [("Planned", lambda r: e(r.get("plannedFor"))), ("Audience", lambda r: e(r["audience"])),
            ("Objective", lambda r: e(r["objective"])), ("Status", lambda r: e(r["status"])),
            ("Claims to verify", lambda r: e(r.get("claimsToVerify"))),
            ("Draft", lambda r: draft_box((r.get("hook", "") + "\n\n" + r.get("body", "") + ("\n\n" + r["cta"] if r.get("cta") else "")).strip(), "Copy post")),
            ("Published", lambda r: e(r.get("publicationEvidence")))]),
        "Validation": table(R["interviews"], [("Participant", lambda r: pname(r["prospectId"])),
            ("State", lambda r: e(r["schedulingState"])), ("Notes", lambda r: e(r["notesProvenance"])),
            ("Findings", lambda r: e(r.get("findings"))), ("Commitments", lambda r: e(r.get("commitments")))],
            "Validation interviews not started." + (" (feature off)" if prefs.get("validation_interviews") == "off" else "")),
        "Jobs": f"""<p class="muted">Applications this week: {e(st['applicationsThisWeek'])} of {e(st['applicationsTarget'])} planned.
Pipeline: {e(', '.join(f'{k} {v}' for k, v in st['jobPipeline'].items()) or 'empty')}</p>""" +
            table(sorted(R["jobs"], key=lambda r: (JOB_STAGES.index(r["stage"]), -r["fitScore"])),
            [("Role", lambda r: e(r["title"])), ("Company", lambda r: e(r["company"])), ("Fit", lambda r: e(r["fitScore"])),
             ("Why / gaps", lambda r: e(r["fitReason"]) + (f"<br><span class='muted'>Gaps: {e(r.get('gaps'))}</span>" if r.get("gaps") else "")),
             ("Stage", lambda r: e(r["stage"])), ("Applied", lambda r: e(r.get("appliedAt"))),
             ("Post", lambda r: f'<a href="{html.escape(r["postingUrl"])}" target="_blank" rel="noopener noreferrer">Open</a>'
              if linkedin_job_id(r.get("postingUrl")) else e(None))],
            "No job posts yet. Ask Claude for today's LinkedIn job search links, then paste the posts you like."),
        "Sales": f"""<p class="muted">Pipeline: {e(', '.join(f'{k} {v}' for k, v in st['dealPipeline'].items()) or 'empty')}</p>""" +
            table(sorted(R["deals"], key=lambda r: (DEAL_STAGES.index(r["stage"]), r.get("nextStepDue") or "")),
            [("Buyer", lambda r: pname(r["prospectId"])), ("Offer", lambda r: e(r["offer"])), ("Stage", lambda r: e(r["stage"])),
             ("Next step", lambda r: e(r["nextStep"])), ("Due", lambda r: e(r.get("nextStepDue"))),
             ("Value", lambda r: e(r.get("value")))],
            "No deals yet. Deals start when a conversation shows a real need."),
        "Opportunities": table(R["opportunities"], [("Type", lambda r: e(r["type"])), ("Contact", lambda r: pname(r.get("prospectId"))),
            ("Org", lambda r: e(r.get("organization"))), ("Stage", lambda r: e(r["stage"])),
            ("Next", lambda r: e(r.get("nextAction"))), ("Outcome", lambda r: e(r["outcome"]))]),
        "Progress": table(funnel_metrics, [("Period", lambda r: e(r["period"])), ("Metric", lambda r: e(r["name"])),
            ("Value", lambda r: e(r.get("numerator")) + (f" / {e(r.get('denominator'))}" if r.get("denominator") is not None else "")),
            ("Calculation", lambda r: e(r["calculation"])), ("Source", lambda r: e(r["source"]))],
            "No metrics yet. Unknown values are shown as unknown, never zero."),
        "Settings": "<p class='muted'>Settings live in <code>settings/PREFERENCES.md</code>. Change them by editing that file "
                    "or telling Claude e.g. <code>set minutes_per_day 20</code>.</p>" +
                    table([{"k": k, "v": v} for k, v in prefs.items()], [("Key", lambda r: e(r["k"])), ("Value", lambda r: e(r["v"]))]),
    }
    alerts = [*st["preferenceIssues"], *st["dataProblems"]]
    alerts += [f"Run failed: {f['job']} {f['runKey']} — {f.get('note') or ''}" for f in st["recentFailures"]]
    alerts += [f"Stale research: {', '.join(st['staleResearch'])}"] if st["staleResearch"] else []
    alert_html = "".join(f"<li>{e(a)}</li>" for a in alerts)
    last = st["lastSuccessfulRun"]
    nav = "".join(f'<button role="tab" data-v="{k}">{k}</button>' for k in sections)
    views = "".join(f'<section id="v-{k}" class="view" hidden><h2>{k}</h2>{v}</section>' for k, v in sections.items())
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>LinkedIn Copilot</title><style>
:root{{--bg:#f6f7f9;--surface:#fff;--text:#1b1f24;--muted:#5d6672;--line:#dfe3e8;--accent:#0a66c2;--warn:#b54708;--warnbg:#fff4e5}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0f1216;--surface:#171b21;--text:#e6e9ee;--muted:#9aa4b1;--line:#2a313a;--accent:#5aa9ff;--warn:#f6b36b;--warnbg:#2b2117}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
.wrap{{max-width:1100px;margin:0 auto;padding:16px}}header.top{{display:flex;flex-wrap:wrap;gap:8px 24px;align-items:baseline;justify-content:space-between}}
h1{{font-size:20px;margin:0}}.meta{{color:var(--muted);font-size:13px}}nav{{display:flex;gap:4px;overflow-x:auto;margin:16px 0;border-bottom:1px solid var(--line)}}
nav button{{background:none;border:0;border-bottom:2px solid transparent;color:var(--muted);padding:8px 10px;font:inherit;cursor:pointer;white-space:nowrap}}
nav button[aria-selected=true]{{color:var(--text);border-color:var(--accent)}}h2{{font-size:18px}}h3{{font-size:15px;margin:0}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px;margin:0 0 12px}}.card header{{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}}
.pill{{font-size:12px;padding:1px 7px;border-radius:99px;background:var(--accent);color:#fff}}.muted,.hint{{color:var(--muted)}}.hint{{font-size:13px}}
.next{{background:var(--surface);border-left:4px solid var(--accent);padding:12px 14px;border-radius:8px;margin-bottom:16px;display:grid}}.next span{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}
.draft{{position:relative;margin:8px 0}}pre{{white-space:pre-wrap;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:10px;margin:0;font:13px/1.5 ui-monospace,Consolas,monospace;max-width:60ch}}
.copy,.btn{{font:inherit;font-size:13px;padding:5px 10px;border-radius:6px;border:1px solid var(--line);background:var(--surface);color:var(--accent);cursor:pointer;text-decoration:none;margin-top:6px;display:inline-block}}
.row{{display:flex;gap:12px;align-items:center;flex-wrap:wrap}}.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;background:var(--surface);font-size:14px}}
th,td{{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:var(--muted);font-weight:600;font-size:12px}}
.unk{{color:var(--muted);font-style:italic}}.alerts{{background:var(--warnbg);color:var(--warn);border-radius:8px;padding:8px 14px 8px 30px;margin:12px 0}}
dl.kv{{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px}}dt{{color:var(--muted)}}dd{{margin:0}}code{{font-size:12.5px}}
</style></head><body><div class="wrap">
<header class="top"><h1>LinkedIn Copilot</h1><div class="meta">Rendered {e(st['localTime'])} · Stage: {e(st['stage'])} ·
Last successful run: {e(last and (last.get('job', '') + ' ' + last.get('finishedAt', '')))} · Background prep: {e(st['backgroundPreparation'])}</div></header>
{f'<ul class="alerts">{alert_html}</ul>' if alert_html else ''}
<p class="meta">Read-only snapshot generated from <code>data/*.json</code>. Drafts are never sent or published by this system — you act in LinkedIn, then confirm in chat.</p>
<nav role="tablist">{nav}</nav>{views}</div>
<script>
const tabs=[...document.querySelectorAll('nav button')];
function show(v){{tabs.forEach(b=>b.setAttribute('aria-selected',b.dataset.v===v));document.querySelectorAll('.view').forEach(s=>s.hidden=s.id!=='v-'+v);try{{localStorage.setItem('lc-tab',v)}}catch(e){{}}}}
tabs.forEach(b=>b.onclick=()=>show(b.dataset.v));let t='Today';try{{t=localStorage.getItem('lc-tab')||t}}catch(e){{}}show(tabs.some(b=>b.dataset.v===t)?t:'Today');
document.querySelectorAll('.copy').forEach(b=>b.onclick=async()=>{{const txt=b.previousElementSibling.textContent;try{{await navigator.clipboard.writeText(txt);b.textContent='Copied'}}catch(e){{const r=document.createRange();r.selectNodeContents(b.previousElementSibling);getSelection().removeAllRanges();getSelection().addRange(r);b.textContent='Selected — press Ctrl+C'}}setTimeout(()=>b.textContent='Copy',2000)}});
</script></body></html>"""
    atomic_write(DASHBOARD, page)
    print(json.dumps({"ok": True, "dashboard": str(DASHBOARD)}))

# --------------------------------------------------------------------------- cli


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("prefs")
    sp = sub.add_parser("set-pref"); sp.add_argument("key"); sp.add_argument("value", nargs="+")
    sub.add_parser("validate")
    g = sub.add_parser("get"); g.add_argument("file"); g.add_argument("--id"); g.add_argument("--where", nargs="*", default=[])
    n = sub.add_parser("next-id"); n.add_argument("file")
    u = sub.add_parser("upsert"); u.add_argument("file"); u.add_argument("--file", dest="src", required=True)
    u.add_argument("--expect-revision", type=int); u.add_argument("--actor", default="ai", choices=["ai", "user"])
    s = sub.add_parser("status"); s.add_argument("--minutes", type=int)
    sub.add_parser("followups")
    ju = sub.add_parser("jobs-url"); ju.add_argument("--keywords", required=True); ju.add_argument("--location", default="")
    sub.add_parser("apply-features")
    r = sub.add_parser("run"); r.add_argument("action", choices=["start", "finish", "fail", "skip"])
    r.add_argument("--job", required=True); r.add_argument("--key"); r.add_argument("--note")
    r.add_argument("--period", choices=["day", "week", "month"], default="day")
    sub.add_parser("dashboard")
    rs = sub.add_parser("restore"); rs.add_argument("file"); rs.add_argument("--revision", type=int, required=True)
    a = ap.parse_args()

    if a.cmd == "init":
        created = []
        for name in FILES:
            if not path_of(name).exists():
                atomic_write(path_of(name), json.dumps(empty_doc(), indent=2) + "\n")
                created.append(name)
        print(json.dumps({"ok": True, "created": created}))
    elif a.cmd == "prefs":
        v, issues = load_prefs()
        print(json.dumps({"preferences": v, "issues": issues}, indent=2, ensure_ascii=False))
    elif a.cmd == "set-pref":
        val = set_pref(a.key, " ".join(a.value))
        print(json.dumps({"ok": True, a.key: val}))
        if a.key in FEATURES:
            apply_features()
    elif a.cmd == "validate":
        prefs, issues = load_prefs()
        probs = validate_all(load_all(), prefs)
        print(json.dumps({"ok": not probs, "dataProblems": probs, "preferenceIssues": issues}, indent=2, ensure_ascii=False))
        sys.exit(2 if probs else 0)
    elif a.cmd == "get":
        doc = load(a.file)
        recs = doc["records"]
        if a.id:
            recs = [r for r in recs if r["id"] == a.id]
        for w in a.where:
            k, _, v = w.partition("=")
            recs = [r for r in recs if str(r.get(k)).lower() == v.lower()]
        print(json.dumps({"revision": doc["revision"], "records": recs}, indent=2, ensure_ascii=False))
    elif a.cmd == "next-id":
        print(next_id(a.file, load(a.file)))
    elif a.cmd == "upsert":
        raw = sys.stdin.read() if a.src == "-" else Path(a.src).read_text(encoding="utf-8")
        upsert(a.file, json.loads(raw), a.expect_revision, a.actor)
    elif a.cmd == "status":
        print(json.dumps(compute_status(a.minutes), indent=2, ensure_ascii=False))
    elif a.cmd == "jobs-url":
        prefs, _ = load_prefs()
        print(json.dumps({"url": linkedin_jobs_url(a.keywords, a.location, prefs),
                          "note": "Give this link to the student to open. Do not load or read it yourself."}))
    elif a.cmd == "followups":
        prefs, _ = load_prefs()
        print(json.dumps(compute_followups(load_all(), prefs), indent=2, ensure_ascii=False))
    elif a.cmd == "apply-features":
        apply_features()
    elif a.cmd == "run":
        run_cmd(a.action, a.job, a.key, a.note, a.period)
    elif a.cmd == "dashboard":
        render_dashboard()
    elif a.cmd == "restore":
        src = BACKUPS / f"{a.file}.r{a.revision}.json"
        if not src.exists():
            die(f"no backup {src.name}")
        with Lock():
            save(a.file, json.loads(src.read_text(encoding="utf-8")))
        print(json.dumps({"ok": True, "restoredFrom": src.name}))


if __name__ == "__main__":
    main()
