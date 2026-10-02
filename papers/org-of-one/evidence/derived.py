# /// script
# requires-python = "==3.11.*"
# dependencies = []
# ///
"""Derived numbers for paper 1. Usage: derived.py [OUT.json]   (default: derived.json here)

Pure arithmetic over the other evidence files in this directory: no git, no network, no
department repo read, nothing random. Each output key names its inputs in `_inputs`.
Written by paper-writer, 2026-10-02, for numbers the draft states that no single evidence
key holds (shares, spans, time to a department's first merged node, repos active in the
same hour). Re-running gives byte-identical output.
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

EV = Path(__file__).resolve().parent
load = lambda n: json.loads((EV / f"{n}.json").read_text())
scale, integ, life, state, inc, leads = (load(n) for n in (
    "scale", "integrations", "lifecycle", "studio_state", "incidents", "leads"))
ts = datetime.fromisoformat
hours = lambda a, b: round((ts(b) - ts(a)).total_seconds() / 3600, 2)

out = {"_note": "derived by derived.py from the evidence JSON beside it; arithmetic only",
       "_inputs": {}}


def put(key, value, inputs):
    out[key] = value
    out["_inputs"][key] = inputs


org, st = scale["org"], scale["repos"]["studio"]
put("org_span_hours", hours(org["first_commit"], org["last_commit"]),
    "scale.org.first_commit, scale.org.last_commit")
put("studio_span_hours", hours(st["first_commit"], st["last_commit"]),
    "scale.repos.studio.first_commit, .last_commit")
put("org_coauthor_share", round(org["commits_with_claude_coauthor"] / org["commits"], 3),
    "scale.org.commits_with_claude_coauthor / scale.org.commits")
put("studio_coauthor_share", round(st["commits_with_claude_coauthor"] / st["commits"], 3),
    "scale.repos.studio.commits_with_claude_coauthor / .commits")
put("org_commits_on_2026_10_02_share",
    round(org["commits_per_day"]["2026-10-02"] / org["commits"], 3),
    "scale.org.commits_per_day['2026-10-02'] / scale.org.commits")
born_last_day = sorted(r for r, t in org["department_first_commit"].items()
                       if t.startswith("2026-10-02"))
put("repos_first_commit_on_2026_10_02", born_last_day, "scale.org.department_first_commit")

si = integ["repos"]["studio"]
put("studio_hand_resolved_share",
    round(si["merges_needing_hand_resolution_remerge_diff"] / si["merges"], 3),
    "integrations.repos.studio.merges_needing_hand_resolution_remerge_diff / .merges")
put("studio_hand_resolved_graph_share",
    round(si["hand_resolved_merges_touching_class"]["graph.yaml (board)"]
          / si["merges_needing_hand_resolution_remerge_diff"], 3),
    "integrations.repos.studio.hand_resolved_merges_touching_class['graph.yaml (board)'] / "
    "merges_needing_hand_resolution_remerge_diff")
only_graph = sum(1 for m in si["hand_resolved_merges"] if m["classes"] == ["graph.yaml (board)"])
put("studio_hand_resolved_only_graph", only_graph,
    "integrations.repos.studio.hand_resolved_merges[].classes == ['graph.yaml (board)']")
hand_trunk_into_branch = si["merge_kinds"]["trunk into branch (by hand)"]
put("studio_hand_resolved_share_of_hand_trunk_merges",
    round(si["merges_needing_hand_resolution_by_kind"]["trunk into branch (by hand)"]
          / hand_trunk_into_branch, 3),
    "integrations...merges_needing_hand_resolution_by_kind['trunk into branch (by hand)'] / "
    "merge_kinds['trunk into branch (by hand)']")

# Time from a department's first commit to its first node reaching `merged` on the board.
first_merged = {}
for repo, r in life["repos"].items():
    times = [n["reached"]["merged"] for n in r["per_node"] if "merged" in n.get("reached", {})]
    if times:
        first = min(times, key=ts)
        first_merged[repo] = {"first_commit": org["department_first_commit"][repo],
                              "first_node_merged": first,
                              "hours": hours(org["department_first_commit"][repo], first)}
put("hours_first_commit_to_first_merged_node", first_merged,
    "scale.org.department_first_commit; lifecycle.repos.*.per_node[].reached.merged")

# Repositories with at least one commit in the same clock hour (not sessions: a session can
# commit in another repo, e.g. studio's lead-9 set up kits elsewhere).
per_hour = Counter()
for repo, r in scale["repos"].items():
    for h, n in r.get("commits_per_hour", {}).items():
        if n:
            per_hour[h] += 1
mx = max(per_hour.values())
put("max_repos_committing_in_one_hour", {"repos": mx,
    "hours": sorted(h for h, v in per_hour.items() if v == mx)},
    "scale.repos.*.commits_per_hour")

# Observational: PASS markers against studio nodes merged or deployed at the pin.
fs = life["repos"]["studio"]["final_state_counts"]
put("studio_nodes_merged_or_deployed_at_pin", fs["merged"] + fs["deployed"],
    "lifecycle.repos.studio.final_state_counts merged + deployed")
put("studio_pass_markers_for_board_nodes", state["pass_markers"]["markers_for_board_nodes"],
    "studio_state.pass_markers.markers_for_board_nodes (OBSERVATIONAL)")

# Studio nodes merged or deployed at the pin whose board history never shows `merged`
# (first seen as deployed, or moved straight from building to deployed): 104 - 100.
skipped = sorted(n["id"] for n in life["repos"]["studio"]["per_node"]
                 if n["final_state"] in ("merged", "deployed") and "merged" not in n["reached"])
put("studio_nodes_deployed_without_merged_state", {"count": len(skipped), "nodes": skipped},
    "lifecycle.repos.studio.per_node[] final_state in (merged, deployed), no reached.merged")

# Named lead sessions across the org: the highest number per department (lead-1..N).
# design-manufacture-interface has no entry: no factory-lead-N appears anywhere.
hi = leads["highest_number_by_department"]
put("named_lead_sessions_org", {"total": sum(hi.values()), "by_department": hi,
    "departments_without_named_leads": sorted(set(scale["repos"]) - set(hi))},
    "leads.highest_number_by_department (sum); scale.repos keys minus those")

# Incidents: distinct incidents whose lesson came from studio, and the share of copies.
cnt = inc["counts"]
put("lessons_copied_share", round(cnt["copied_or_same_event"] / cnt["dated_lessons"], 3),
    "incidents.counts.copied_or_same_event / dated_lessons")
put("studio_attributed_span_hours_median",
    sorted(v["hours"] for v in leads["repos"]["studio"]["session_spans_from_attributed_commits"]
           .values())[len(leads["repos"]["studio"]["session_spans_from_attributed_commits"]) // 2],
    "leads.repos.studio.session_spans_from_attributed_commits[].hours (upper median of 12)")

dest = Path(sys.argv[1]) if len(sys.argv) > 1 else EV / "derived.json"
dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "_inputs"}, indent=1))
