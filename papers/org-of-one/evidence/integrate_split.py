# /// script
# requires-python = "==3.11.*"
# dependencies = []
# ///
"""Which studio merges could the integration script have made? Usage:
    nice -n 10 uv run --python 3.11 --script integrate_split.py --repo <studio checkout or clone> [OUT.json]

Git-only and read-only (`git log`, `git rev-parse`; no merge, no object written), at studio's
pin from sources.json. Runs none of studio's code. Written by paper-writer, 2026-10-02, for
the peer review of paper 1 (M1): integrate.sh makes two merges per node, a trunk-into-branch
merge (subject "Merge main into X (integrate N)", counted in integrations.json) and a
`--no-ff` branch-into-trunk merge with subject "Merge <branch>: <title> (<node>)". The
second form can also be typed by hand, so the count below is "has the script's form after
the script reached trunk", an upper bound on the script's own merges, not proof.

Outputs (default integrate_split.json beside this file):
- integrate_sh_reached_trunk: the first first-parent commit at the pin whose tree has
  scripts/lead/integrate.sh (sha, committer date);
- branch_into_trunk: 130 merges split before/after that time, and how many after it have
  the script's subject form;
- trunk_into_branch_by_hand: split before/after;
- hand_resolved_not_trunk_into_branch: the 4 hand-resolved merges that are not hand merges of
  trunk into a branch (from integrations.json), each marked before/after the script.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

EV = Path(__file__).resolve().parent
args = sys.argv[1:]
repo = Path(args[args.index("--repo") + 1])
rest = [a for i, a in enumerate(args) if a != "--repo" and (i == 0 or args[i - 1] != "--repo")]
dest = Path(rest[0]) if rest else EV / "integrate_split.json"
pin = json.loads((EV / "sources.json").read_text())["repos"]["studio"]["main"]
integ = json.loads((EV / "integrations.json").read_text())["repos"]["studio"]

# Same subject rules as mine.py.
INTEGRATE_RE = re.compile(r"^Merge (?:main|trunk) into (\S+) \(integrate (\S+?)\)")
TRUNK_INTO_RE = re.compile(r"^Merge (?:(?:remote-tracking )?branch '(?:main|trunk|origin/main)'"
                           r"|(?:main|trunk)) into ")
NODE_MERGE_RE = re.compile(r"^Merge (?:branch ')?([^\s:']+)'?(?::| into main\b)")
SCRIPT_FORM_RE = re.compile(r"^Merge \S+: .+ \(([^()\s]+)\)$")


def git(*a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True,
                          text=True).stdout


assert git("rev-parse", pin).strip() == pin, "pin not found in --repo"
first_parent = git("rev-list", "--first-parent", pin).split()
fp = set(first_parent)
reached = git("log", "--first-parent", "--reverse", "--format=%H %cI", pin, "--",
              "scripts/lead/integrate.sh").splitlines()[0].split()
t_script = datetime.fromisoformat(reached[1])

rows = git("log", "--merges", "--format=%H%x1f%cI%x1f%s", pin).splitlines()
b2t = {"before": 0, "after": 0, "after_with_script_subject_form": 0}
t2b_hand = {"before": 0, "after": 0}
t2b_script = 0
for row in rows:
    sha, when, subj = row.split("\x1f")
    side = "after" if datetime.fromisoformat(when) >= t_script else "before"
    if INTEGRATE_RE.match(subj):
        t2b_script += 1
    elif TRUNK_INTO_RE.match(subj):
        t2b_hand[side] += 1
    elif sha in fp and NODE_MERGE_RE.match(subj):
        b2t[side] += 1
        if side == "after" and SCRIPT_FORM_RE.match(subj):
            b2t["after_with_script_subject_form"] += 1

others = []
for m in integ["hand_resolved_merges"]:
    if m["kind"] != "trunk into branch (by hand)":
        when = datetime.fromisoformat(m["date"])
        others.append({"sha": m["sha"], "kind": m["kind"], "date": m["date"],
                       "relative_to_script": "after" if when >= t_script else "before"})
others.sort(key=lambda r: r["date"])

out = {
    "_note": "git-only, read-only, studio at the pin in sources.json; see the docstring",
    "studio_pin": pin,
    "integrate_sh_reached_trunk": {"sha": reached[0][:9], "committer_date": reached[1]},
    "branch_into_trunk": dict(b2t, total=b2t["before"] + b2t["after"]),
    "trunk_into_branch_by_hand": dict(t2b_hand, total=t2b_hand["before"] + t2b_hand["after"]),
    "trunk_into_branch_by_integrate_script": t2b_script,
    "hand_resolved_not_trunk_into_branch": others,
}
dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(json.dumps(out, indent=1))
