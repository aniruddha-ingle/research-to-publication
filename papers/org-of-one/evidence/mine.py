# /// script
# requires-python = "==3.11.*"
# dependencies = []
# ///
"""Mine the org's COMMITTED git history for paper 1 ("An org of one"). Stdlib only.

Usage (from anywhere; nice it, the machine is shared):
  nice -n 10 uv run --python 3.11 --script mine.py --clones <scratch dir> [--pins sources.json]

What it does, and what it never does:
- It reads the eight department repos only to (a) `git rev-parse` their trunk and (b) clone
  them, bare and without hardlinks, into --clones (a scratch dir). Every other git command
  runs in those clones at the pinned SHAs, so nothing is ever written in a department's repo
  (not even the temporary objects `--remerge-diff` creates). Working trees are never read and
  no department's code is run.
- Without --pins it pins each repo's `main` (and mir-triage's `board`, where its graph lives)
  as it is now and writes sources.json. With --pins it re-mines at the recorded SHAs.
- Outputs (JSON, text only, next to this script): sources.json, scale.json, leads.json,
  lifecycle.json, integrations.json, structure.json.

Privacy: node ids and branch names are replaced by neutral ids (department + sequence of
first appearance + a coarse kind) because some carry the client's or a track's name. No
commit subject, author name or e-mail is written out; only counts, dates, SHAs and lead
session names (lead-N style, which are role names, not people).
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")  # the Mac's zone; every commit is -04:00 (checked below)
BOARD = "claude-plans/graph.yaml"

# repo, short name, board ref (None: no graph), own lead-name prefix, lead playbook path
REPOS = [
    ("studio", "studio", "main", "lead", ".claude/skills/lead-playbook/SKILL.md"),
    ("mir-triage", "mir", "board", "mir-triage-lead", ".claude/skills/mir-research/SKILL.md"),
    ("copy-in-product-picture", "copy", "main", "copy-lead", ".claude/skills/copy-lead/SKILL.md"),
    ("product-in-picture", "pip", None, "pip-lead", ".claude/skills/pip-lead/SKILL.md"),
    ("product-in-video", "piv", "main", "piv-lead", ".claude/skills/piv-lead/SKILL.md"),
    ("design-manufacture-interface", "dmi", "main", "factory-lead",
     ".claude/skills/factory-lead/SKILL.md"),
    ("gateway", "gateway", None, "gateway", ".claude/skills/gateway-lead/SKILL.md"),
    ("research-to-publication", "research", "main", "research-lead",
     ".claude/skills/research-lead/SKILL.md"),
]
PREFIX_TO_DEPT = {p: name for name, _, _, p, _ in REPOS}

# A lead session name anywhere in text: an optional department prefix, then lead-N/gateway-N.
LEAD_RE = re.compile(r"(?<![A-Za-z0-9_-])((?:[a-z]+-)*?(?:lead|gateway))-(\d+)\b")
COAUTHOR_RE = re.compile(r"^Co-Authored-By:\s*(Claude[^<]*?)\s*<", re.M | re.I)
STATES = ["todo", "claimed", "building", "built", "review", "ready", "merged", "deployed",
          "dropped"]


def git(repo: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} in {repo}: {r.stderr.strip()}")
    return r.stdout


def when(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def day(dt: datetime) -> str:
    return dt.astimezone(TZ).date().isoformat()


def iso(dt: datetime) -> str:
    return dt.astimezone(TZ).isoformat()


def hours(a: datetime, b: datetime) -> float:
    return round((b - a).total_seconds() / 3600, 3)


def summary(xs: list[float]) -> dict:
    if not xs:
        return {"n": 0}
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4, method="inclusive") if len(xs) > 1 else [xs[0]] * 3
    return {"n": len(xs), "min": xs[0], "p25": round(q[0], 3), "median": round(q[1], 3),
            "p75": round(q[2], 3), "max": xs[-1], "mean": round(statistics.fmean(xs), 3)}


def find_org(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "studio").is_dir() and (p / "gateway").is_dir():
            return p
    sys.exit("can't find the org root (a dir holding studio/ and gateway/); pass --org")


# ---- pinning and clones -------------------------------------------------------------------

def pin_and_clone(org: Path, clones: Path, pins_file: Path | None, out: Path) -> dict:
    clones.mkdir(parents=True, exist_ok=True)
    pins = json.loads(pins_file.read_text()) if pins_file else None
    sources = {"mined_with": "papers/org-of-one/evidence/mine.py", "timezone": str(TZ),
               "git": git(org / "studio", "--version").strip(), "repos": {}}
    for name, _, board_ref, _, _ in REPOS:
        src = org / name
        clone = clones / f"{name}.git"
        if not clone.exists():
            subprocess.run(["git", "clone", "--bare", "--no-hardlinks", "--quiet", str(src),
                            str(clone)], check=True)
        else:  # refresh the scratch clone from the source (reads the source only)
            git(clone, "fetch", "--quiet", "--force", str(src), "+refs/heads/*:refs/heads/*")
        refs = {"main": None}
        if board_ref and board_ref != "main":
            refs[board_ref] = None
        for ref in refs:
            sha = pins["repos"][name][ref] if pins else git(src, "rev-parse", ref).strip()
            if git(clone, "cat-file", "-t", sha, check=False).strip() != "commit":
                sys.exit(f"{name}: pinned {ref} {sha} is not in the clone")
            refs[ref] = sha
        sources["repos"][name] = refs
    if pins:
        sources["mined_at"] = pins.get("mined_at")
    else:
        sources["mined_at"] = datetime.now(TZ).replace(microsecond=0).isoformat()
    (out / "sources.json").write_text(json.dumps(sources, indent=2, sort_keys=True) + "\n")
    return sources


# ---- commits ------------------------------------------------------------------------------

def commits(clone: Path, sha: str) -> list[dict]:
    raw = git(clone, "log", sha, "--format=%H%x1f%P%x1f%aI%x1f%cI%x1f%ae%x1f%B%x1e")
    out = []
    for rec in raw.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        h, parents, a, c, ae, body = rec.split("\x1f", 5)
        out.append({"sha": h, "parents": parents.split(), "author": when(a),
                    "committer": when(c), "author_id": ae, "msg": body.strip()})
    return out


def first_parent(clone: Path, sha: str) -> set[str]:
    return set(git(clone, "rev-list", "--first-parent", sha).split())


def scale_for(name: str, cs: list[dict], fp: set[str]) -> dict:
    merges = [c for c in cs if len(c["parents"]) > 1]
    co = [c for c in cs if COAUTHOR_RE.search(c["msg"])]
    models = Counter()
    for c in cs:
        for m in set(COAUTHOR_RE.findall(c["msg"])):
            models[m.strip()] += 1
    per_day = Counter(day(c["committer"]) for c in cs)
    per_hour = Counter(c["committer"].astimezone(TZ).strftime("%Y-%m-%dT%H") for c in cs)
    offsets = Counter(c["committer"].strftime("%z") for c in cs)
    span = [min(c["committer"] for c in cs), max(c["committer"] for c in cs)]
    graph_commits = sum(1 for c in cs if c["msg"].startswith("Graph:"))
    return {
        "commits": len(cs),
        "merges": len(merges),
        "non_merge_commits": len(cs) - len(merges),
        "first_parent_commits_on_main": len(fp),
        "first_parent_merges_on_main": sum(1 for c in merges if c["sha"] in fp),
        "commits_with_claude_coauthor": len(co),
        "commits_without_claude_coauthor": len(cs) - len(co),
        "coauthor_commits_by_model": dict(sorted(models.items())),
        "commits_with_graph_subject": graph_commits,
        "distinct_authors": len({c.get("author_id") for c in cs}),
        "first_commit": iso(span[0]),
        "last_commit": iso(span[1]),
        "active_days": len(per_day),
        "commits_per_day": dict(sorted(per_day.items())),
        "commits_per_hour": dict(sorted(per_hour.items())),
        "committer_utc_offsets": dict(offsets),
        "author_date_differs_from_committer_date": sum(
            1 for c in cs if c["author"] != c["committer"]),
    }


# ---- lead sessions ------------------------------------------------------------------------

def lead_names(text: str) -> list[tuple[str, str]]:
    """(prefix, name) for every lead session name in the text."""
    found = []
    for m in LEAD_RE.finditer(text):
        prefix, n = m.group(1), m.group(2)
        # keep the longest known prefix that the match ends with (e.g. "for-mir-triage-lead")
        best = None
        for p in PREFIX_TO_DEPT:
            if prefix == p or prefix.endswith("-" + p):
                if best is None or len(p) > len(best):
                    best = p
        if best is None:
            best = "?" + prefix
        found.append((best, f"{best}-{n}" if best != "lead" else f"lead-{n}"))
    return found


def attribute(msg: str, own: str) -> tuple[str | None, str | None]:
    """(strict, loose) attribution of a commit to one of its repo's own lead sessions.
    strict: a parenthetical in the SUBJECT starts with exactly one own lead's name (studio's
    convention: "Graph: x ready (lead-9)", "(lead-1 inline; ...)", "(lead-13 sign-off)"), and
    not a possessive ("lead-1's" is about that lead, not by it). loose: the whole message
    names exactly one own lead, in any role. Only strict is used for session spans."""
    subj = msg.splitlines()[0] if msg else ""
    strict_names = set()
    for m in re.finditer(r"\(\s*((?:[a-z]+-)*?(?:lead|gateway)-\d+)(?!['\u2019]|\d)", subj):
        for p, nm in lead_names(m.group(1)):
            if p == own:
                strict_names.add(nm)
    strict = strict_names.pop() if len(strict_names) == 1 else None
    names = {nm for p, nm in lead_names(msg) if p == own}
    loose = names.pop() if len(names) == 1 else None
    return strict, loose


def concurrency(spans: dict[str, tuple[datetime, datetime]]) -> dict:
    """Leads whose [first, last] attributed-commit span covers each hour; max per day."""
    if not spans:
        return {}
    start = min(s for s, _ in spans.values()).astimezone(TZ).replace(minute=0, second=0)
    end = max(e for _, e in spans.values())
    per_hour, t = {}, start
    while t <= end:
        t2 = t + timedelta(hours=1)
        per_hour[t.strftime("%Y-%m-%dT%H")] = sum(1 for s, e in spans.values()
                                                  if s < t2 and e >= t)
        t = t2
    per_day = defaultdict(int)
    for h, n in per_hour.items():
        per_day[h[:10]] = max(per_day[h[:10]], n)
    # the exact maximum overlap of spans (sweep line)
    ev = sorted([(s, 1) for s, _ in spans.values()] + [(e, -1) for _, e in spans.values()],
                key=lambda x: (x[0], -x[1]))
    cur = best = 0
    for _, d in ev:
        cur += d
        best = max(best, cur)
    return {"max_overlap": best, "max_per_day": dict(sorted(per_day.items())),
            "per_hour": per_hour}


def leads_for(name: str, short: str, own: str, clone: Path, sha: str, cs: list[dict],
              mentions: dict) -> dict:
    strict_c, loose_c = Counter(), Counter()
    times: dict[str, list[datetime]] = defaultdict(list)
    hourly_active: dict[str, set] = defaultdict(set)
    for c in cs:
        for p, nm in lead_names(c["msg"]):
            mentions["commit_messages"][p].add(nm)
        s, lo = attribute(c["msg"], own)
        if s:
            strict_c[s] += 1
            times[s].append(c["committer"])
            hourly_active[c["committer"].astimezone(TZ).strftime("%Y-%m-%dT%H")].add(s)
        if lo:
            loose_c[lo] += 1
    # committed files at the pin (plans, notes, playbooks, boards): every lead name in them
    grep = git(clone, "grep", "-I", "-h", "-o", "-E", r"([a-z]+-)*(lead|gateway)-[0-9]+",
               sha, "--", "*.md", "*.yaml", "*.yml", "*.txt", check=False)
    in_files = set()
    for line in grep.splitlines():
        for p, nm in lead_names(line):
            in_files.add((p, nm))
            mentions["committed_files"][p].add(nm)
    spans = {k: (min(v), max(v)) for k, v in times.items()}
    per_day_active = defaultdict(set)
    for k, v in times.items():
        for t in v:
            per_day_active[day(t)].add(k)
    own_in_files = sorted({nm for p, nm in in_files if p == own}, key=lead_key)
    return {
        "own_prefix": own,
        "own_leads_in_commit_messages": sorted(set(loose_c) | set(strict_c), key=lead_key),
        "own_leads_in_committed_files": own_in_files,
        "attributed_commits_strict": dict(sorted(strict_c.items(), key=lambda x: lead_key(x[0]))),
        "attributed_commits_loose": dict(sorted(loose_c.items(), key=lambda x: lead_key(x[0]))),
        "attributed_share_strict": round(sum(strict_c.values()) / len(cs), 4) if cs else 0,
        "attributed_share_loose": round(sum(loose_c.values()) / len(cs), 4) if cs else 0,
        "session_spans_from_attributed_commits": {
            k: {"first": iso(s), "last": iso(e), "hours": hours(s, e), "commits": strict_c[k]}
            for k, (s, e) in sorted(spans.items(), key=lambda x: lead_key(x[0]))},
        "distinct_leads_with_attributed_commits_per_day": {
            d: sorted(v, key=lead_key) for d, v in sorted(per_day_active.items())},
        "max_distinct_leads_committing_in_one_hour": max(
            (len(v) for v in hourly_active.values()), default=0),
        "max_distinct_leads_committing_in_one_hour_per_day": {
            d: max(len(v) for h, v in hourly_active.items() if h.startswith(d))
            for d in sorted({h[:10] for h in hourly_active})},
        "concurrency_from_spans": concurrency(spans),
    }


def lead_key(nm: str) -> tuple:
    m = re.search(r"(\d+)$", nm)
    return (nm.rsplit("-", 1)[0], int(m.group(1)) if m else 0)


# ---- board lifecycles ---------------------------------------------------------------------

def parse_board(text: str) -> dict[str, str]:
    nodes, cur = {}, None
    for line in text.splitlines():
        m = re.match(r'^\s*- id:\s*"?([^"\s#]+)', line)
        if m:
            cur = m.group(1)
            nodes[cur] = "?"
            continue
        m = re.match(r'^\s+state:\s*"?([A-Za-z]+)', line)
        if m and cur:
            nodes[cur] = m.group(1)
    return nodes


def node_kind(node_id: str) -> str:
    if re.match(r"^p\d", node_id):
        return "plan"
    first = node_id.split("-")[0]
    return {"bl": "backlog", "fix": "fix", "ops": "ops", "req": "request", "exp": "experiment",
            "perf": "perf", "docs": "docs", "org": "org", "research": "research"}.get(first,
                                                                                      "other")


def lifecycles(short: str, clone: Path, ref_sha: str) -> dict:
    # --full-history: keep side-branch commits that changed the board even when the merge
    # took the trunk's copy; each commit is diffed against its FIRST parent's board.
    raw = git(clone, "log", "--full-history", "--reverse", ref_sha,
              "--format=%H%x1f%P%x1f%cI", "--", BOARD)
    events, first_seen, order = [], {}, []
    cache: dict[str, dict] = {}

    def board_at(sha: str) -> dict:
        if sha not in cache:
            t = git(clone, "show", f"{sha}:{BOARD}", check=False)
            cache[sha] = parse_board(t)
        return cache[sha]

    n_commits = 0
    for line in raw.splitlines():
        h, parents, c = line.split("\x1f")
        n_commits += 1
        t = when(c)
        now = board_at(h)
        before = board_at(parents.split()[0]) if parents else {}
        for nid, st in now.items():
            if nid not in first_seen:
                first_seen[nid] = (t, st)
                order.append(nid)
            if before.get(nid) != st:
                events.append((t, nid, before.get(nid), st, h))
    final = board_at(ref_sha)
    # Regressions: on the board ref's first-parent line, a node's state moving BACK (e.g.
    # ready -> building): a lost update or a deliberate reopen. dropped/removed don't count.
    rank = {st: i for i, st in enumerate(STATES[:-1])}
    fp = set(git(clone, "rev-list", "--first-parent", ref_sha).split())
    regressions = [(t, nid, a, b, h) for t, nid, a, b, h in events
                   if h in fp and a in rank and b in rank and rank[b] < rank[a]]
    neutral = {nid: f"{short}-n{i + 1:03d}" for i, nid in enumerate(order)}

    reach: dict[str, dict[str, datetime]] = defaultdict(dict)
    for t, nid, _, st, _ in events:
        if st not in reach[nid] or t < reach[nid][st]:
            reach[nid][st] = t
    nodes, dist = [], defaultdict(list)
    for nid in order:
        r = reach[nid]
        t0, s0 = first_seen[nid]
        rec = {"id": neutral[nid], "kind": node_kind(nid), "first_state": s0,
               "first_seen": iso(t0), "final_state": final.get(nid, "removed"),
               "reached": {s: iso(r[s]) for s in STATES if s in r}}
        m = r.get("merged")

        def first_of(*ss):
            ts = [r[s] for s in ss if s in r]
            return min(ts) if ts else None

        if m:
            started = first_of("claimed", "building")
            rev = first_of("review", "ready")
            built = first_of("built")
            lt = {}
            if s0 == "todo":
                lt["todo_to_merged_h"] = hours(t0, m)
            lt["first_seen_to_merged_h"] = hours(t0, m)
            if started and started <= m:
                lt["claimed_to_merged_h"] = hours(started, m)
            if built and built <= m:
                lt["built_to_merged_h"] = hours(built, m)
            if rev and rev <= m:
                lt["review_to_merged_h"] = hours(rev, m)
            rec["lead_times"] = lt
            for k, v in lt.items():
                dist[k].append(v)
        if "deployed" in r and m:
            rec["merged_to_deployed_h"] = hours(m, r["deployed"])
            dist["merged_to_deployed_h"].append(hours(m, r["deployed"]))
        nodes.append(rec)
    # a node seeded in a later state ("merged" on its first appearance) has no lead time
    merged_nodes = [n for n in nodes if "merged" in n["reached"]]
    return {
        "board_ref_sha": ref_sha,
        "board_commits_full_history": n_commits,
        "transition_events": len(events),
        "nodes": len(nodes),
        "first_state_counts": dict(Counter(n["first_state"] for n in nodes)),
        "final_state_counts": dict(Counter(n["final_state"] for n in nodes)),
        "kind_counts": dict(Counter(n["kind"] for n in nodes)),
        "ever_merged": len(merged_nodes),
        "ever_dropped": sum(1 for n in nodes if "dropped" in n["reached"]),
        "merged_on_first_appearance": sum(1 for n in merged_nodes
                                          if n["reached"]["merged"] == n["first_seen"]),
        "state_regressions_on_trunk": len(regressions),
        "state_regressions_on_trunk_list": [
            {"date": iso(t), "node": neutral[nid], "from": a, "to": b, "sha": h[:9]}
            for t, nid, a, b, h in regressions],
        "lead_time_hours": {k: summary(v) for k, v in sorted(dist.items())},
        "lead_time_hours_values": {k: sorted(v) for k, v in sorted(dist.items())},
        "per_node": nodes,
    }


# ---- integrations -------------------------------------------------------------------------

INTEGRATE_RE = re.compile(r"^Merge (?:main|trunk) into (\S+) \(integrate (\S+?)\)")
TRUNK_INTO_RE = re.compile(r"^Merge (?:(?:remote-tracking )?branch '(?:main|trunk|origin/main)'"
                           r"|(?:main|trunk)) into ")
NODE_MERGE_RE = re.compile(r"^Merge (?:branch ')?([^\s:']+)'?(?::| into main\b)")
GENERATED = ("schema.d.ts", "openapi.json")


def conflict_files(clone: Path, sha: str) -> list[str]:
    """Files a clean automatic re-merge would have left different (git --remerge-diff):
    the merge needed a hand resolution (or changed something on top)."""
    out = git(clone, "show", "--remerge-diff", "--format=", "--name-only", sha, check=False)
    return sorted({ln for ln in out.splitlines() if ln.strip()})


def file_class(path: str) -> str:
    if path == BOARD:
        return "graph.yaml (board)"
    if "agent-memory" in path:
        return "agent memory"
    if path.endswith(GENERATED) or "/generated/" in path:
        return "generated file"
    top = path.split("/")[0]
    if top in ("claude-plans", "docs") or path.endswith(".md"):
        return "plans and docs"
    return "code and config"


def integrations_for(clone: Path, cs: list[dict], fp: set[str]) -> dict:
    merges = [c for c in cs if len(c["parents"]) > 1]
    kinds = Counter()
    trunk_into = by_integrate = 0
    msg_conflicts, remerge = [], []
    conflict_classes = Counter()
    per_day_integrations = Counter()
    for c in merges:
        subj = c["msg"].splitlines()[0]
        if INTEGRATE_RE.match(subj):
            by_integrate += 1
            trunk_into += 1
            k = "trunk into branch (integrate script)"
        elif TRUNK_INTO_RE.match(subj):
            trunk_into += 1
            k = "trunk into branch (by hand)"
        elif c["sha"] in fp and NODE_MERGE_RE.match(subj):
            k = "branch into trunk"
            per_day_integrations[day(c["committer"])] += 1
        elif c["sha"] in fp:
            k = "other merge on trunk"
        else:
            k = "other merge off trunk"
        kinds[k] += 1
        if re.search(r"conflict|main's copy|theirs|ours\b", c["msg"], re.I):
            msg_conflicts.append({"sha": c["sha"][:9], "date": iso(c["committer"]), "kind": k})
        files = conflict_files(clone, c["sha"])
        if files:
            classes = sorted({file_class(f) for f in files})
            for cl in classes:
                conflict_classes[cl] += 1
            remerge.append({"sha": c["sha"][:9], "date": iso(c["committer"]), "kind": k,
                            "files": len(files), "classes": classes})
    nonmerge_conflict_mentions = sum(
        1 for c in cs if len(c["parents"]) < 2 and re.search(r"conflict", c["msg"], re.I))
    return {
        "merges": len(merges),
        "merge_kinds": dict(sorted(kinds.items())),
        "trunk_into_branch_merges": trunk_into,
        "trunk_into_branch_by_integrate_script": by_integrate,
        "branch_into_trunk_per_day": dict(sorted(per_day_integrations.items())),
        "merges_whose_message_mentions_a_conflict": len(msg_conflicts),
        "merges_whose_message_mentions_a_conflict_list": msg_conflicts,
        "non_merge_commits_mentioning_conflict": nonmerge_conflict_mentions,
        "merges_needing_hand_resolution_remerge_diff": len(remerge),
        "merges_needing_hand_resolution_by_kind": dict(Counter(r["kind"] for r in remerge)),
        "hand_resolved_merges_touching_class": dict(sorted(conflict_classes.items())),
        "hand_resolved_merges": remerge,
    }


# ---- the 3-lead trial (studio plan 06, recorded in 6b04ffe) -----------------------------

TRIAL_RECORD = "6b04ffe3e06c89db6ca533d050b6eb2235b3147a"
# The record's own times: lead-1 from 00:37Z, lead-2 until ~01:40Z, lead-3 from 01:39Z
# (2026-09-30 UTC). The window ends at the record commit's merge of p06-trial.
TRIAL_START = datetime(2026, 9, 30, 0, 37, tzinfo=timezone.utc)


def trial_check(clone: Path, sha: str, cs: list[dict], fp: set[str], integ: dict,
                life: dict, leads: dict) -> dict:
    rec = git(clone, "show", "-s", "--format=%cI", TRIAL_RECORD)
    end = when(rec.strip()) + timedelta(seconds=20)  # p06-trial merged 19 s after the record
    inwin = [c for c in cs if TRIAL_START <= c["committer"] <= end]
    hand = [m for m in integ["hand_resolved_merges"] if TRIAL_START <= when(m["date"]) <= end]
    regress = [r for r in life["state_regressions_on_trunk_list"]
               if TRIAL_START <= when(r["date"]) <= end]
    merged = [n for n in life["per_node"]
              if "merged" in n["reached"] and TRIAL_START <= when(n["reached"]["merged"]) <= end]
    strict = Counter()
    for c in inwin:
        s, _ = attribute(c["msg"], "lead")
        if s:
            strict[s] += 1
    # File overlap between the nodes merged in the window: files each merged branch changed
    # (merge-base diff), leaving out the shared indexes plan 06 merges at integration.
    shared = (BOARD, "claude-plans/01-review-app.md", "CLAUDE.md", "docs/README.md")
    changed = {}
    for c in inwin:
        if len(c["parents"]) > 1 and c["sha"] in fp and NODE_MERGE_RE.match(
                c["msg"].splitlines()[0]):
            fs = git(clone, "diff", "--name-only", f"{c['parents'][0]}...{c['parents'][1]}")
            changed[c["sha"]] = {f for f in fs.splitlines()
                                 if f not in shared and "agent-memory" not in f}
    keys = list(changed)
    overlaps = sorted({f for i, a in enumerate(keys) for b in keys[i + 1:]
                       for f in changed[a] & changed[b]})
    redo = [c["sha"][:9] for c in inwin
            if re.search(r"overwritten|again \(", c["msg"].splitlines()[0])]
    return {
        "record_commit": TRIAL_RECORD[:9],
        "record_is_ancestor_of_pin": git(clone, "merge-base", "--is-ancestor", TRIAL_RECORD,
                                         sha, check=False) == "",
        "window_utc": [TRIAL_START.isoformat(), end.astimezone(timezone.utc).isoformat()],
        "window_hours": hours(TRIAL_START, end),
        "commits": len(inwin),
        "merges": sum(1 for c in inwin if len(c["parents"]) > 1),
        "branch_into_trunk_merges": sum(1 for c in inwin if len(c["parents"]) > 1
                                        and c["sha"] in fp
                                        and NODE_MERGE_RE.match(c["msg"].splitlines()[0])),
        "nodes_reaching_merged": len(merged),
        "files_changed_by_more_than_one_merged_branch_excl_shared_indexes": len(overlaps),
        "overlapping_file_classes": dict(Counter(file_class(f) for f in overlaps)),
        "merges_needing_hand_resolution": len(hand),
        "state_regressions_on_trunk": len(regress),
        "graph_state_reset_after_overwrite_commits": redo,
        "strictly_attributed_commits_by_lead": dict(sorted(strict.items())),
    }


# ---- structure: the kit and the lessons ---------------------------------------------------

KIT_FILES = ["scripts/lead/graph.py", "scripts/lead/claim.sh", "scripts/lead/with-lock.sh",
             "scripts/lead/integrate.sh", "scripts/lead/hooks/pre-push"]


def lessons(text: str) -> dict:
    m = re.search(r"^## Lessons.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    body = m.group(1) if m else ""
    items = re.findall(r"^- (\d{4}-\d{2}-\d{2})(?: \(([^)]*)\))? ·", body, re.M)
    inherited = [x for x in items if x[1].startswith("from ")]
    return {"has_lessons_section": bool(m), "dated_lessons": len(items),
            "inherited_from_another_repo": len(inherited),
            "from_the_user": sum(1 for x in items if x[1] == "the user"),
            "own": len(items) - len(inherited),
            "by_date": dict(sorted(Counter(d for d, _ in items).items()))}


def structure_for(clone: Path, sha: str, board_ref: str | None, playbook: str,
                  board_sha: str | None) -> dict:
    files = set(git(clone, "ls-tree", "-r", "--name-only", sha).splitlines())
    board_files = files
    if board_sha and board_sha != sha:
        board_files = set(git(clone, "ls-tree", "-r", "--name-only", board_sha).splitlines())
    pb = git(clone, "show", f"{sha}:{playbook}", check=False)
    return {
        "kit_files_present": {f: f in files for f in KIT_FILES},
        "has_lead_kit": all(f in files for f in KIT_FILES[:4]),
        "board_file": BOARD if BOARD in board_files else None,
        "board_ref": board_ref,
        "lead_playbook": playbook if pb else None,
        "lessons": lessons(pb),
        "agents_defined": sorted(Path(f).stem for f in files
                                 if f.startswith(".claude/agents/") and f.endswith(".md")),
    }


def handoff_kits(clone: Path, sha: str) -> list[str]:
    out = git(clone, "ls-tree", "-d", "--name-only", sha, "claude-plans/handoffs/", check=False)
    return sorted(Path(p).name for p in out.splitlines())


# ---- main ---------------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--org", type=Path, default=None, help="the org root (holds studio/ ...)")
    ap.add_argument("--clones", type=Path, required=True, help="scratch dir for bare clones")
    ap.add_argument("--pins", type=Path, default=None, help="re-mine at these SHAs")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    org = a.org or find_org(Path(__file__).resolve().parent)
    sources = pin_and_clone(org, a.clones, a.pins, a.out)

    scale, leads, life, integ, struct = {}, {}, {}, {}, {}
    mentions = {"commit_messages": defaultdict(set), "committed_files": defaultdict(set)}
    all_commits = []
    for name, short, board_ref, own, playbook in REPOS:
        clone = a.clones / f"{name}.git"
        sha = sources["repos"][name]["main"]
        cs = commits(clone, sha)
        fp = first_parent(clone, sha)
        print(f"{name}: {len(cs)} commits at {sha[:9]}", file=sys.stderr)
        scale[name] = scale_for(name, cs, fp)
        all_commits += [(name, c) for c in cs]
        leads[name] = leads_for(name, short, own, clone, sha, cs, mentions)
        board_sha = sources["repos"][name].get(board_ref) if board_ref else None
        if board_ref:
            life[name] = lifecycles(short, clone, board_sha)
            if board_ref != "main":  # the board branch's own commits are lead commits too
                bcs = commits(clone, board_sha)
                scale[name]["board_branch_commits_not_on_main"] = len(
                    {c["sha"] for c in bcs} - {c["sha"] for c in cs})
        integ[name] = integrations_for(clone, cs, fp)
        struct[name] = structure_for(clone, sha, board_ref, playbook, board_sha)
        if name == "studio":
            struct[name]["handoff_kits"] = handoff_kits(clone, sha)
            integ[name]["trial_2026_09_30"] = trial_check(clone, sha, cs, fp, integ[name],
                                                          life[name], leads[name])

    # org totals
    tot = {k: sum(scale[r][k] for r in scale) for k in
           ("commits", "merges", "commits_with_claude_coauthor")}
    tot["first_commit"] = min(scale[r]["first_commit"] for r in scale)
    tot["last_commit"] = max(scale[r]["last_commit"] for r in scale)
    per_day = Counter()
    for _, c in all_commits:
        per_day[day(c["committer"])] += 1
    tot["commits_per_day"] = dict(sorted(per_day.items()))
    tot["repos"] = len(scale)
    tot["department_first_commit"] = {r: scale[r]["first_commit"] for r in scale}
    scale_out = {"_note": "committed history at the SHAs in sources.json; dates are committer "
                          "dates in America/New_York; the user is the only git author",
                 "org": tot, "repos": scale}

    by_dept = defaultdict(set)
    ambiguous = defaultdict(set)
    for where, d in mentions.items():
        for p, names in d.items():
            dept = PREFIX_TO_DEPT.get(p) if p != "?" else None
            for nm in names:
                if dept:
                    by_dept[dept].add(nm)
                else:
                    ambiguous[p].add(nm)
    leads_out = {
        "_note": "lead session names (role names like lead-9) seen in committed history. "
                 "strict attribution = a parenthetical in the subject starts with exactly one of "
                 "the repo's own leads, e.g. '(lead-9)'; loose = the message names exactly one "
                 "own lead in any role. Session spans run from a lead's first to last STRICTLY "
                 "attributed commit; concurrency counts spans covering an "
                 "hour. A lead that committed nothing attributable is invisible here.",
        "lead_names_by_department_anywhere": {
            d: sorted(v, key=lead_key) for d, v in sorted(by_dept.items())},
        "highest_number_by_department": {
            d: max(lead_key(n)[1] for n in v) for d, v in sorted(by_dept.items())},
        "unclassified_names": {p: sorted(v) for p, v in ambiguous.items()},
        "repos": leads,
    }
    struct_out = {"_note": "files present at the pinned SHA; lessons counted as dated bullets "
                           "in the lead playbook's Lessons section",
                  "repos_with_lead_kit": sorted(r for r in struct if struct[r]["has_lead_kit"]),
                  "repos_with_board": sorted(r for r in struct if struct[r]["board_file"]),
                  "dated_lessons_total": sum(s["lessons"]["dated_lessons"]
                                             for s in struct.values()),
                  "dated_lessons_own_total": sum(s["lessons"]["own"] for s in struct.values()),
                  "repos": struct}
    life_out = {"_note": "node state transitions from each board's git history "
                         "(--full-history, each commit against its first parent); a node's "
                         "time in a state is the FIRST commit that shows it there. Node ids "
                         "are neutral (department + order of first appearance).",
                "repos": life}
    integ_out = {"_note": "merge commits at the pin. hand resolution = git show "
                          "--remerge-diff is non-empty (a clean re-merge would differ), run in "
                          "a scratch clone.", "repos": integ}
    for fname, obj in [("scale.json", scale_out), ("leads.json", leads_out),
                       ("lifecycle.json", life_out), ("integrations.json", integ_out),
                       ("structure.json", struct_out)]:
        (a.out / fname).write_text(json.dumps(obj, indent=1, sort_keys=True,
                                              default=str) + "\n")
        print(f"wrote {fname}", file=sys.stderr)


if __name__ == "__main__":
    main()
