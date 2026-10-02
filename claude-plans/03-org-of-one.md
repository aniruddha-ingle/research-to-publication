# 03 · Paper 1: "An org of one" (research-lead-1, 2026-10-02)

Node `paper-1`, gate full. Picked by the user (00-organisation.md, "The user's answers").

## The claim, in one sentence
One engineer ran a working multi-department software organisation for a week as concurrent
LLM (Claude) lead sessions on a single laptop, coordinated only through git: a plan-first
feature graph, atomic filesystem claims, one locked integration gate, reviewer agents that
never edit, and a gateway that carries direction but never approval. Its failures were
concrete and recurring, and each was fixed by a rule written back into the repo.

## Why it is new (related work: see docs/inventory.md §1)
MetaGPT, ChatDev and recent multi-agent coding studies (e.g. arXiv 2608.16801) measure role
pipelines or synthetic runs on benchmark tasks. This is a longitudinal case study of a *live*
org: real products, one human steering, every decision and incident in git. Framed as an
**observational case study / experience report plus one small trial**, not a controlled
experiment. No speed-up or cost claims (nothing was recorded; studio's answer in the inventory).

## Evidence (all to be mined and recounted here; nothing quoted from the inventory unchecked)
| Evidence | Source | How |
|---|---|---|
| Design of the system | studio plan 06, ADR 0024, `scripts/lead/` in each repo | read at pinned SHAs |
| Scale: commits, merges, co-author lines, lead numbers, departments | `git log` of all 8 repos at pinned SHAs | count script, committed |
| Node lifecycles: states, lead time todo→merged, review→merged | `graph.yaml` history of every repo | mining script over `git log -p` |
| Integrations, conflicts, merges of trunk | integrate commit messages | mining script |
| 3-lead trial | studio `6b04ffe` | quoted, checked |
| Incidents (25+) | each repo's lead-playbook Lessons | coded by hand into a taxonomy (cause, harm, fix, rule) committed as text |
| Review gate | PASS markers (studio `.worktrees/.state/pass/`, read-only by studio's agreement) | aggregate counts only |
| Deploys | studio live-history.log, autodeploy.log (read-only by studio's agreement) | aggregate counts only |
| Governance | `../CLAUDE.md`, gateway docs, each department's CLAUDE.md | quoted, scrubbed |

Pinned SHAs are recorded in `papers/org-of-one/evidence/sources.json` when mined.

## Figures (each from a script in papers/org-of-one/figures/ reading evidence/*.json)
1. Timeline: commits/day and concurrent leads per repo across the week.
2. Node lifecycle: lead time distribution (todo→merged) per department.
3. Incident taxonomy: counts by cause class, with the rule each produced.
4. Architecture diagram (TikZ or a script, no data).

## Private and withheld
No Haki data, Devin's media, licensed audio or track names. Names scrubbed: Devin, Steph,
the CEO/COO, Haki ("the client"). Session transcripts and reviewer screenshots are not used
(the user's call, not asked). Studio's state is read only for aggregates and quoted lines,
never `shots/`, never touching `locks/`. Evidence files hold counts, SHAs, dates and node ids.

## Venue
arXiv-style preprint draft first, then an agents or software-engineering workshop. Kept in
`article` until a workshop is named; then vendor its style. Nothing submitted without the user.

## Steps
1. reproducer: mine evidence → `papers/org-of-one/evidence/`, figure scripts.
2. paper-writer: draft from template, every number from evidence.
3. peer-reviewer: full gate. Fix Blocker/Major.
4. The user reads the draft (people gate); the gateway is told it builds.

## Open questions (recommendations; nothing waits on them)
1. Acknowledgements: rec. none beyond the AI-assistance statement until the user says.
2. Which workshop: rec. decide once a draft exists; the lead lists 2–3 with deadlines.
