# /// script
# requires-python = "==3.11.*"
# dependencies = []
# ///
"""Check incidents.json against the committed lead playbooks at the pins. Stdlib only.

Usage (after mine.py made the clones):
  uv run --python 3.11 --script check_incidents.py --clones <scratch dir>

Checks: every dated lesson in every repo's lead playbook (Lessons section) at the pinned
SHA is coded exactly once, with the date as written; each record's `added_in` commit is in
the pinned history and changed the playbook; every `same_event_as` names a record; the
counts block matches the records; no record names the client, its people or the org's
executives. Exit status 1 on any failure.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mine  # noqa: E402

SHORT = {name: short for name, short, *_ in mine.REPOS}
PLAYBOOK = {name: pb for name, _, _, _, pb in mine.REPOS}
DENY = re.compile(r"\b(haki|tracklib|devin|steph|ceo|coo)\b", re.I)


def dated_lessons(sources: dict, clones: Path) -> dict:
    """{(short, ordinal): (date, tag)} for every dated lesson at the pins."""
    found = {}
    for name, refs in sources.items():
        text = mine.git(clones / f"{name}.git", "show", f"{refs['main']}:{PLAYBOOK[name]}")
        m = re.search(r"^## Lessons.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
        items = re.findall(r"^- (\d{4}-\d{2}-\d{2})(?: \(([^)]*)\))? ·", m.group(1), re.M)
        for i, (d, tag) in enumerate(items, 1):
            found[(SHORT[name], i)] = (d, tag)
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clones", type=Path, required=True)
    here = Path(__file__).resolve().parent
    a = ap.parse_args()
    sources = json.loads((here / "sources.json").read_text())["repos"]
    inc = json.loads((here / "incidents.json").read_text())
    found = dated_lessons(sources, a.clones)
    bad = []
    coded = Counter()
    ids = {r["id"] for r in inc["lessons"]}
    for r in inc["lessons"]:
        short, n = r["id"].rsplit("-", 1)
        key = (short, int(n))
        coded[key] += 1
        if key not in found:
            bad.append(f"{r['id']}: no such dated lesson at the pin")
            continue
        if found[key][0] != r["date"]:
            bad.append(f"{r['id']}: date {r['date']} != playbook {found[key][0]}")
        src = r["source"]
        clone = a.clones / f"{src['repo']}.git"
        pin = sources[src["repo"]]["main"]
        if mine.git(clone, "merge-base", "--is-ancestor", src["added_in"], pin,
                    check=False) != "":
            bad.append(f"{r['id']}: added_in {src['added_in']} not in the pinned history")
        if src["path"] not in mine.git(clone, "show", "--name-only", "--format=",
                                       src["added_in"], check=False):
            bad.append(f"{r['id']}: added_in {src['added_in']} did not change {src['path']}")
        if r["same_event_as"] and r["same_event_as"] not in ids:
            bad.append(f"{r['id']}: same_event_as {r['same_event_as']} is not a record")
        text = " ".join(str(v) for k, v in r.items() if k != "source")
        if DENY.search(text):
            bad.append(f"{r['id']}: names someone or something private")
    for key in found:
        if coded[key] != 1:
            bad.append(f"{key}: coded {coded[key]} times")
    if inc["counts"]["dated_lessons"] != len(found):
        bad.append(f"counts.dated_lessons {inc['counts']['dated_lessons']} != {len(found)}")
    own = [r for r in inc["lessons"] if r["same_event_as"] is None]
    if inc["counts"]["distinct_events_or_rules"] != len(own):
        bad.append("counts.distinct_events_or_rules is stale")
    for e in inc["coordination_events_from_history"]:
        if DENY.search(e["description"]):
            bad.append(f"{e['id']}: names someone or something private")
        for sha in e["evidence"]:
            if mine.git(a.clones / "studio.git", "merge-base", "--is-ancestor", sha,
                        sources["studio"]["main"], check=False) != "":
                bad.append(f"{e['id']}: {sha} not in studio's pinned history")
    print(f"{len(found)} dated lessons at the pins, {len(inc['lessons'])} coded, "
          f"{len(own)} distinct; {len(bad)} problems")
    for b in bad:
        print("  " + b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
