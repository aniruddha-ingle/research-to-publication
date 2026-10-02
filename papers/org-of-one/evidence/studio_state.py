# /// script
# requires-python = "==3.11.*"
# dependencies = []
# ///
"""Aggregate studio's UNCOMMITTED state for paper 1: observational evidence, not history.

Usage (after mine.py, which made the clones and sources.json):
  nice -n 10 uv run --python 3.11 --script studio_state.py --clones <scratch dir>

Read-only, by studio's agreement (lead-9, 2026-10-02; docs/inventory.md, "studio's
agreement"). It reads:
  studio/.worktrees/.state/pass/        PASS markers (file name = node, content = SHA)
  studio/.worktrees/.state/claims/      live claims (counted)
  studio/.worktrees/.state/resources/   reserved numbers (lead-N, plan-N, adr-N, migration-N)
  studio/.worktrees/.state/locks/       live mutexes: the entries are COUNTED by listing the
                                        directory, nothing in it is opened, created or removed
  studio/.worktrees/.state/live-history.log
  ~/.sample-staging/logs/autodeploy.log
It never opens studio/.worktrees/.state/shots/. It writes only studio_state.json next to
itself: counts, dates, distributions, and neutral node ids (the same mapping as mine.py).
These files change while studio runs, so the numbers are a snapshot at `read_at`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mine  # noqa: E402  (the same board parser and neutral-id order)

TZ = mine.TZ


def neutral_ids(clone: Path, sha: str) -> tuple[dict, dict]:
    raw = mine.git(clone, "log", "--full-history", "--reverse", sha, "--format=%H", "--",
                   mine.BOARD).split()
    order = []
    for h in raw:
        for nid in mine.parse_board(mine.git(clone, "show", f"{h}:{mine.BOARD}")):
            if nid not in order:
                order.append(nid)
    return ({nid: f"studio-n{i + 1:03d}" for i, nid in enumerate(order)},
            mine.parse_board(mine.git(clone, "show", f"{sha}:{mine.BOARD}")))


def mtime(p: Path) -> datetime:
    return datetime.fromtimestamp(p.stat().st_mtime, TZ)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", type=Path, default=None)
    ap.add_argument("--clones", type=Path, required=True)
    ap.add_argument("--deploy-log", type=Path,
                    default=Path.home() / ".sample-staging/logs/autodeploy.log")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    org = a.org or mine.find_org(Path(__file__).resolve().parent)
    state = org / "studio/.worktrees/.state"
    sources = json.loads((a.out / "sources.json").read_text())
    pin = sources["repos"]["studio"]["main"]
    clone = a.clones / "studio.git"
    neutral, final = neutral_ids(clone, pin)
    main_commits = set(mine.git(clone, "rev-list", pin).split())

    # PASS markers
    pass_dir = state / "pass"
    markers = sorted(p for p in pass_dir.iterdir() if p.is_file())
    per_node, per_day = [], Counter()
    for p in markers:
        sha = p.read_text().strip()
        t = mtime(p)
        per_day[t.date().isoformat()] += 1
        full = mine.git(clone, "rev-parse", "--verify", "--quiet", sha + "^{commit}",
                        check=False).strip()
        per_node.append({
            "node": neutral.get(p.name, "not-on-board"),
            "marker_written": t.isoformat(timespec="minutes"),
            "sha_is_a_commit_in_history": bool(full),
            "sha_reachable_from_main_pin": full in main_commits,
            "node_state_at_pin": final.get(p.name, "not-on-board"),
        })
    per_node.sort(key=lambda r: r["marker_written"])
    pin_time = datetime.fromisoformat(mine.git(clone, "show", "-s", "--format=%cI", pin).strip())
    pass_out = {
        "markers": len(markers),
        "markers_written_by_pin_commit_time": sum(
            1 for r in per_node if datetime.fromisoformat(r["marker_written"]) <= pin_time),
        "pin_commit_time": pin_time.isoformat(),
        "per_day_by_mtime": dict(sorted(per_day.items())),
        "first": per_node[0]["marker_written"] if per_node else None,
        "last": per_node[-1]["marker_written"] if per_node else None,
        "markers_for_board_nodes": sum(1 for r in per_node if r["node"] != "not-on-board"),
        "sha_reachable_from_main_pin": sum(r["sha_reachable_from_main_pin"] for r in per_node),
        "node_state_at_pin": dict(Counter(r["node_state_at_pin"] for r in per_node)),
        "per_node": per_node,
    }

    # claims, resources, locks (counts only for claims and locks)
    claims = [p for p in (state / "claims").iterdir() if p.is_dir()]
    lock_entries = len(os.listdir(state / "locks"))
    res = sorted(p for p in (state / "resources").iterdir() if p.is_dir())
    kinds = Counter(re.sub(r"-\d+$", "", p.name) for p in res)
    nums = {k: sorted(int(p.name.rsplit("-", 1)[1]) for p in res
                      if re.sub(r"-\d+$", "", p.name) == k) for k in kinds}
    lead_res = {}
    for p in res:
        if re.fullmatch(r"lead-\d+", p.name):
            since = (p / "since").read_text().strip()
            lead_res[p.name] = datetime.fromtimestamp(int(since), TZ).isoformat()
    lead_res = dict(sorted(lead_res.items(), key=lambda x: mine.lead_key(x[0])))

    # session spans: start = number reserved, end = last strictly attributed commit
    leads = json.loads((a.out / "leads.json").read_text())["repos"]["studio"]
    spans = {}
    for nm, start in lead_res.items():
        s = leads["session_spans_from_attributed_commits"].get(nm)
        if s:
            spans[nm] = (datetime.fromisoformat(start), datetime.fromisoformat(s["last"]))
    conc = mine.concurrency(spans)

    # live-history.log
    lh = (state / "live-history.log").read_text().splitlines()
    deploys = [ln.split() for ln in lh if len(ln.split()) > 2 and ln.split()[1] == "deploy"]
    lh_days = Counter(d[0][:10] for d in deploys)
    overlay = sum(1 for d in deploys if len(d) > 3 and d[3].startswith("main=")
                  and d[2] != d[3][5:])
    live_out = {
        "lines": len(lh), "deploy_lines": len(deploys),
        "first": deploys[0][0] if deploys else None, "last": deploys[-1][0] if deploys else None,
        "per_utc_day": dict(sorted(lh_days.items())),
        "deployed_sha_differs_from_main_sha": overlay,
        "deployed_sha_equals_main_sha": len(deploys) - overlay,
    }

    # autodeploy.log
    al = a.deploy_log.read_text().splitlines()
    kind = Counter()
    fail_reasons = Counter()
    overlays, overlay_nodes = 0, set()
    for ln in al:
        m = re.match(r"^(\d{4}-\d{2}-\d{2}T\S+Z) (.*)$", ln)
        if not m:
            kind["untimestamped (shell error)"] += 1
            continue
        rest = m.group(2)
        k = rest.split(":")[0] if rest.startswith(("deploying", "migrating", "migrated")) else \
            " ".join(rest.split()[:2])
        if rest.startswith("deploy FAILED"):
            k = "deploy FAILED"
            reason = rest.split(":", 1)[1].strip()
            fail_reasons["doctor failed" if reason.startswith("doctor") else
                         "database not at migration head" if "migration head" in reason else
                         "other"] += 1
        elif rest.startswith("deployed "):
            k = "deployed"
            if " + " in rest:
                overlays += 1
                for nm in re.findall(r"\+ ([A-Za-z0-9._/-]+)", rest):
                    overlay_nodes.add(nm)
        kind[k] += 1
    times = [re.match(r"^(\S+Z) ", ln).group(1) for ln in al if re.match(r"^\S+Z ", ln)]
    deploy_out = {
        "lines": len(al), "first": times[0] if times else None,
        "last": times[-1] if times else None,
        "line_kinds": dict(sorted(kind.items())),
        "failed_deploys_by_reason": dict(fail_reasons),
        "deploys_with_built_branches_overlaid": overlays,
        "distinct_built_nodes_overlaid": len(overlay_nodes),
        "quoted_line": "deploy/bin/autodeploy.sh: line 244: syntax error near unexpected "
                       "token `fi'  (the one untimestamped line; path shortened)",
    }

    out = {
        "_note": "OBSERVATIONAL: studio's uncommitted state dir and deploy log, read-only by "
                 "studio's agreement, aggregates only. Not git history; files are rewritten "
                 "while studio runs (a PASS marker's mtime is its LAST write). shots/ never "
                 "opened; locks/ only counted.",
        "read_at": datetime.now(TZ).replace(microsecond=0).isoformat(),
        "studio_main_pin": pin,
        "pass_markers": pass_out,
        "claims_live": len(claims),
        "locks_entries_live": lock_entries,
        "resources_reserved_by_kind": dict(sorted(kinds.items())),
        "resources_numbers_by_kind": nums,
        "lead_number_reserved_at": lead_res,
        "lead_sessions_reserved_to_last_attributed_commit": {
            nm: {"start": s.isoformat(), "end": e.isoformat(),
                 "hours": mine.hours(s, e)} for nm, (s, e) in spans.items()},
        "concurrency_reserved_to_last_commit": conc,
        "live_history": live_out,
        "autodeploy_log": deploy_out,
    }
    (a.out / "studio_state.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("wrote studio_state.json", file=sys.stderr)


if __name__ == "__main__":
    main()
