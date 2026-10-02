---
name: org-history-mining
description: Non-obvious facts about mining the org's git history for paper 1 (org-of-one): where boards live, date conventions, what states mean, how to mine without writing in dept repos
metadata:
  type: project
---

Facts learned mining paper 1's evidence (2026-10-02, papers/org-of-one/evidence/ on branch paper-1):

- mir-triage's board `claude-plans/graph.yaml` lives on its `board` branch, not main. product-in-picture and gateway have no board and no `scripts/lead/`.
- Lead-playbook lesson dates follow UTC (studio "09-30" lessons committed on the evening of 09-29 EDT). mir-triage's 09-28 lessons were back-filled on 10-01.
- In studio, `ready`→merged takes about 30 s because `ready` is set just before integrate.sh. Reviews happen during `building` and leave only PASS markers (studio/.worktrees/.state/pass, uncommitted).
- Only studio names sessions in commit subjects ("(lead-9)"), so lead concurrency is derivable for studio only.
- `git show --remerge-diff` writes temp objects, so the mining runs in bare `--no-hardlinks` clones in scratch, never in a department's repo.
- The repos move while you mine. Pin once (sources.json) and re-mine with `--pins`.
- The dataviz validator needs a newer Node than the Mac's v14: copy it to scratch as .mjs and replace `??=`.

**Why:** these cost time to discover and change how numbers must be read.
**How to apply:** start from mine.py/--pins for any follow-up, and read review/lead-time numbers with these caveats. Related: [[paper-1-evidence]]
