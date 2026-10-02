#!/usr/bin/env python3
"""Install or upgrade the linkedin-copilot working folder into a project.

    python <package>/template/linkedin-copilot/tools/install.py <project_dir>

- First run: copies the template (instructions, settings, tools) to <project_dir>/linkedin-copilot,
  plus the kit's .claude/skills when run from a Student Kit.
- Upgrade (package VERSION newer): refreshes instructions/ and tools/ only. Never touches
  settings/PREFERENCES.md or data/; reports preference keys that are new in this version.
- Running from inside the project's own copy is a no-op.
"""
import json
import re
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
SKILLS_SRC = SRC.parent / ".claude" / "skills"  # present in a Student Kit, absent in a plugin
UPGRADABLE = ["instructions", "tools"]
KEY = re.compile(r"^\s*-\s*([A-Za-z0-9_]+)\s*:", re.M)


def sync_skills(project):
    """Kit mode: copy the kit's skills into the project (replacing older copies of the same skills)."""
    if not SKILLS_SRC.is_dir() or project == SRC.parent:
        return []
    dst = project / ".claude" / "skills"
    dst.mkdir(parents=True, exist_ok=True)
    names = []
    for d in sorted(SKILLS_SRC.iterdir()):
        if (d / "SKILL.md").exists():
            shutil.rmtree(dst / d.name, ignore_errors=True)
            shutil.copytree(d, dst / d.name, ignore=shutil.ignore_patterns("__pycache__"))
            names.append(d.name)
    return names


def version(p):
    try:
        return tuple(int(x) for x in (p / "VERSION").read_text().strip().split("."))
    except (OSError, ValueError):
        return (0,)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    project = Path(sys.argv[1]).resolve()
    dst = project / "linkedin-copilot"
    if dst == SRC:
        print(json.dumps({"ok": True, "action": "none", "reason": "running from the project copy"}))
        return
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".lock", "*.tmp*")
    if not dst.exists():
        shutil.copytree(SRC, dst, ignore=ignore)
        (dst / "data").mkdir(exist_ok=True)
        print(json.dumps({"ok": True, "action": "installed", "path": str(dst), "skills": sync_skills(project),
                          "version": (SRC / "VERSION").read_text().strip()}))
        return
    old, new = version(dst), version(SRC)
    if new <= old:
        print(json.dumps({"ok": True, "action": "none", "reason": "already up to date"}))
        return
    for d in UPGRADABLE:
        shutil.rmtree(dst / d, ignore_errors=True)
        shutil.copytree(SRC / d, dst / d, ignore=ignore)
    shutil.copy2(SRC / "VERSION", dst / "VERSION")
    tmpl = set(KEY.findall((SRC / "settings" / "PREFERENCES.md").read_text(encoding="utf-8")))
    mine = set(KEY.findall((dst / "settings" / "PREFERENCES.md").read_text(encoding="utf-8")))
    print(json.dumps({"ok": True, "action": "upgraded", "from": ".".join(map(str, old)),
                      "to": ".".join(map(str, new)), "updated": UPGRADABLE, "skills": sync_skills(project),
                      "newPreferenceKeys": sorted(tmpl - mine),
                      "note": "settings and data were not changed; add new keys to PREFERENCES.md if wanted"}))


if __name__ == "__main__":
    main()
