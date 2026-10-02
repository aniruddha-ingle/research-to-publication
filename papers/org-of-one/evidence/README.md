# Evidence for paper 1, "An org of one"

Mined by research-to-publication's reproducer on 2026-10-02 (node `paper-1`, plan 03).
Every number the paper uses comes from a file here. Each file says how it was made. This
README gives the command, the pin and the result for each number, and marks every number
that comes from studio's **uncommitted** state as **observational**.

## The pins (`sources.json`)

| Repo | Pinned ref | SHA |
|---|---|---|
| studio | main | `af5aaf24bb47f6e57db8c9d1d92683b0ff48dafc` |
| mir-triage | main | `2599cebb6ab42a9e7e2a8dfbdd3d32c84c6c3da6` |
| mir-triage | board (its `graph.yaml` lives on this branch) | `f0dacfb3e4ff20ef727e3568e0afa55993f6093f` |
| copy-in-product-picture | main | `48f062f500ddbc111b1b33c70153faafb688352c` |
| product-in-picture | main | `c0b095dc9ab6b54fb1d0ce9225f249c122ba351c` |
| product-in-video | main | `8b6f38becc907850ab01e94d18fe0760dd11131a` |
| design-manufacture-interface | main | `8cc1238de6b05c8a0b5f8d9f34e3fef8d47e82e4` |
| gateway | main | `a9a58bdc74ec6687c459cfb912b30841f69280f3` |
| research-to-publication | main | `887dd2c431b22ac414be40f8eabc5d92951fb851` |

These were pinned at 2026-10-02T06:40-04:00. The repos keep moving, so every later run
re-mines at these SHAs.

## Environment and commands

macOS on an Intel Mac, git 2.50.1 (Apple Git-155), Python 3.11 under uv (stdlib only for
the evidence scripts). Nothing is random except the figure jitter (seed 0). `$CLONES` is any
scratch directory.

```bash
cd papers/org-of-one/evidence
# 1. committed history -> sources.json (first run only), scale/leads/lifecycle/integrations/structure.json
nice -n 10 uv run --python 3.11 --script mine.py --clones $CLONES --pins sources.json
# 2. studio's uncommitted state -> studio_state.json   (OBSERVATIONAL; read-only, see below)
nice -n 10 uv run --python 3.11 --script studio_state.py --clones $CLONES
# 3. the hand-coded incidents: verify coverage, dates, sources and scrubbing
uv run --python 3.11 --script check_incidents.py --clones $CLONES   # "61 dated lessons ... 0 problems"
# 4. figures (from the paper dir)
make -C .. figures      # build/figures/{timeline,lifecycle,incidents}.pdf, byte-identical on rebuild
```

`mine.py` reads the department repos only to run `git rev-parse` and to make bare clones
(`--no-hardlinks`) into `$CLONES`. Every other git command runs in those clones at the
pins. No department repo is written to, including the temporary objects that
`--remerge-diff` creates, and no department's code is run. Re-running with `--pins` gave
byte-identical JSON (checked twice).

Dates are committer dates, converted to America/New_York. All 1,750 commits carry -04:00,
and the author date differs from the committer date in only 17 of them.

## Committed history (reproducible from the pins)

### Scale (`scale.json`)
| Number | Result | How |
|---|---|---|
| studio commits | **1,355** | `git log <pin>` (all reachable commits) |
| studio merges | **351** | commits with more than one parent |
| studio commits with a Claude `Co-Authored-By` line | **1,257** (744 "Claude Fable 5.1", 513 "Claude Opus 5.5") | regex `^Co-Authored-By:\s*Claude` per message |
| studio date range | 2026-09-28T18:25 to 2026-10-02T06:22 (-04:00) | min/max committer date |
| studio commits per day | 09-28: 107, 09-29: 356, 09-30: 552, 10-01: 305, 10-02: 35 | by local day |
| org commits (8 repos) | **1,750**, of which 425 merges and 1,635 with a Claude co-author | sum over repos |
| org date range | 2026-09-26T17:34 (mir-triage's first commit) to 2026-10-02T06:40 | |
| per repo: commits / merges / co-author | mir-triage 130/37/114 · copy 144/23/143 · pip 31/4/31 · piv 33/6/33 · dmi 5/0/5 · gateway 29/0/29 · research 23/4/23 | |
| git authors | 1 in every repo (the user). E-mail not recorded. | distinct `%ae` |
| mir-triage board-branch commits not on main | 91 | `board` minus `main` |

### Lead sessions (`leads.json`)
| Number | Result | How |
|---|---|---|
| studio lead numbers in committed files | lead-1 … **lead-13** (13) | `git grep -o` over `*.md *.yaml *.yml *.txt` at the pin |
| studio leads with commits attributed by subject | 12 (all except lead-2) | a parenthetical in the subject starts with exactly one own lead, e.g. `(lead-9)` or `(lead-1 inline; …)`. Possessives like "lead-1's" are excluded |
| studio commits attributed this way | 221 of 1,355 (16.3%) | |
| max concurrent studio leads | **5** (on 10-01) | sweep over each lead's span from first to last attributed commit |
| max studio leads committing within one clock hour | 4 | |
| other departments' lead names anywhere | mir-triage-lead-1…2, copy-lead-1, pip-lead-1…2, piv-lead-1…2, research-lead-1, gateway-1; no factory-lead-N anywhere | same grep plus commit messages, all repos |

Caveat: a span from first to last attributed commit includes idle time, such as a lead
waiting on the user. A lead whose commits never name it is invisible here. Only studio
names its sessions in commit subjects (strict attribution elsewhere: 0), so concurrency is
derivable for studio only.

### Board lifecycles (`lifecycle.json`)
Method: `git log --full-history --reverse <board ref> -- claude-plans/graph.yaml`. Each
commit's board is parsed (`- id:` / `state:`) and diffed against its first parent's board.
A node's time in a state is the first commit that shows it there. Node ids are neutral
(`<dept>-nNNN`, in order of first appearance) with a coarse kind (plan, backlog, fix…).

| Repo | Nodes | Ever merged | Dropped | todo→merged h, median (IQR, n) | claimed/building→merged h, median (n) |
|---|---|---|---|---|---|
| studio | 113 | 100 | 1 | **3.53** (1.38–6.04, 62) | 0.53 (71) |
| mir-triage (board branch) | 41 | 13 | 0 | 1.48 (0.05–1.74, 13) | 1.16 (12) |
| copy-in-product-picture | 37 | 13 | 0 | 1.44 (1.33–1.92, 6) | 1.05 (9) |
| product-in-video | 11 | 3 | 0 | 0.44 (3) | 0.08 (3) |
| research-to-publication | 3 | 2 | 0 | 0.17 (2) | 0.10 (2) |
| design-manufacture-interface | 6 | 0 | 0 | – | – |

- studio `review`/`ready`→merged has a median of 0.008 h (about 30 s, n=92). Studio sets
  `ready` immediately before `integrate.sh`, so this interval measures the integration step,
  not reviewing. Reviews happen while a node is `building`, and their evidence is the PASS
  markers below.
- studio merged→`deployed`: median 0.087 h (about 5 min), n=69. At the pin, 73 studio nodes
  are `deployed`, 31 `merged`, 8 `todo` and 1 `dropped`.
- Backward state moves on the trunk's first-parent line: mir-triage 4 (all
  `review → building` after an evaluator FAIL, i.e. rework rounds), studio 1 (a deliberate
  reopen). Other repos 0.
- 22 studio nodes first appear already `building` (seeded when the board was created), so
  they have no todo time.

### Integrations (`integrations.json`)
| Number | Result | How |
|---|---|---|
| studio branch→trunk merges (first parent, "Merge <node>: …") | 130 | subject regex |
| studio trunk→branch merges | 208 (53 by `integrate.sh`, 155 by hand) | `Merge main into X (integrate X)` vs other `Merge main/branch 'main' into` |
| studio merges that needed a hand resolution | **51** of 351 | `git show --remerge-diff` non-empty, i.e. a clean automatic re-merge would differ |
| … of which touched the board `graph.yaml` | 33 | file class |
| … touched generated files / agent memory / code / plans | 7 / 6 / 14 / 9 | file class (a merge can touch several) |
| … made by `integrate.sh` itself | 0 (it aborts on conflict by design; 47 of the 51 were hand merges of trunk into a branch) | |
| studio merges whose message mentions a conflict ("conflict", "main's copy", "ours", "theirs") | 43 | regex |
| mir-triage / copy hand-resolved merges | 8 / 3 | same |

### The 3-lead trial (`integrations.json` → `studio.trial_2026_09_30`)
Window: from lead-1's start as written in the record (2026-09-30T00:37Z) to p06-trial's
merge, 20 s after the record commit `6b04ffe` (01:52:43Z), 1.26 h in all.
111 commits, 29 merges, 10 branch→trunk merges (the same ten the record lists), 9 board nodes
merged, 2 merges with a hand resolution (one on `graph.yaml`, one on the shared plan 01).
One lost board update (`05ffd0f` overwrote p06-trial's state; `94f8d2d` set it "ready
again"). 8 non-index files were changed by two or more of the merged branches (2 code, 2
generated, 4 docs), all merged by git without conflict. Strictly attributed commits: lead-1
13, lead-3 3, lead-2 0 (it predates session naming).

### Structure and lessons (`structure.json`)
- Full lead kit (`scripts/lead/` graph.py, claim.sh, with-lock.sh, integrate.sh, and
  hooks/pre-push) at the pins in **6 repos**: studio, mir-triage, copy, piv, dmi, research.
  product-in-picture and gateway have a lead playbook but no `scripts/lead/`.
- A board in the same 6 (mir-triage's on its `board` branch).
- Studio's committed kit handoffs (`claude-plans/handoffs/`): 4 (dmi, mir research kit,
  pip kit, piv kit).
- Dated lessons in the 8 lead playbooks: **61** (studio **25**, mir 10, copy 5, pip 9, piv 5,
  dmi 3, gateway 2, research 2).

### Incidents (`incidents.json`, hand-coded; `check_incidents.py` verifies it)
Each of the 61 dated lessons is coded once: kind (incident / practice / the user's
directive), cause class (11 classes, defined in the file), harm, fix, the rule it produced,
and its source (repo, playbook path, pin, ordinal, and `added_in`, the commit that added
it). 15 lessons are copies into another repo or a second lesson about the same event
(`same_event_as`), which leaves **46 distinct**: 33 incidents, 8 practices and 5
directives. Distinct incidents by cause: process/review 10, concurrency/coordination 5,
environment/OS 5, deploy/live safety 4, resource contention 3, tooling defect 2, session
lifecycle 1, communication 1, content policy 1, privacy/data handling 1. The most copied
lesson is studio-22 (a default-parallel test run starved the live Mac), copied into 5 other
repos. Three more coordination events come from commit history (`hist-1..3`, with SHAs).

Lesson dates are as written. They follow UTC: studio's "2026-09-30" lessons 8–14 were
committed on the evening of 09-29 EDT, and mir-triage's 09-28 lessons were written into its
playbook on 10-01 when the kit was ported.

## Observational: studio's uncommitted state (`studio_state.json`)

Read **read-only** by studio's agreement (lead-9, 2026-10-02, recorded in
`docs/inventory.md`). The sources are `studio/.worktrees/.state/{pass,claims,resources,locks}`,
`live-history.log` and `~/.sample-staging/logs/autodeploy.log`. `shots/` was never opened.
`locks/` was only listed and counted. Only aggregates were copied. These files change while
studio runs, so they are a snapshot taken at `read_at` (06:50-04:00), not history.

| Number | Result |
|---|---|
| PASS markers | **78** written by the pin's commit time (79 at read time; one more arrived 06:50 for a node added after the pin). 78 belong to board nodes, and the SHA of every marker is reachable from studio's pinned main. States at the pin: 56 deployed, 22 merged |
| PASS markers per day (by mtime, i.e. last write) | 09-29: 6, 09-30: 40, 10-01: 30, 10-02: 3 |
| reserved numbers (`resources/`) | 55: lead 1–13, plan 8–17, ADR 25–43, migration 5–17 |
| lead-number reservation times | lead-1 2026-09-29T20:37 … lead-13 2026-10-01T13:21 (in the file) |
| max concurrent studio leads, sessions from reservation to last attributed commit | 5 (same as committed history) |
| live claims / lock entries at read time | 1 / 1 |
| live-history deploys | **116** (UTC days 09-30: 62, 10-01: 30, 10-02: 24), 2026-09-30T01:36Z to 10-02T05:31Z. In 33 of them the deployed SHA ≠ main (built branches overlaid, "built = live") |
| autodeploy.log | 116 deploy attempts: 111 deployed, 5 failed (2 health check, 1 database not at migration head, 2 other); 13 migrations; 8 waits for a quiet machine; 5 pauses and 4 resumes; 34 deploys with built branches overlaid (15 distinct nodes) |
| quoted line | `deploy/bin/autodeploy.sh: line 244: syntax error near unexpected token 'fi'` (the log's one untimestamped line; it corroborates lesson studio-15) |

## Withheld (privacy)

- Every node id and branch name is replaced by a neutral id. Some carry the client's name,
  and two in mir-triage look like track or artist names. The mapping is not stored here (the
  scripts recompute the order of first appearance from the repos).
- No commit subject, author name or e-mail, client data, product names or measurements,
  media, audio, track names, session transcripts or reviewer screenshots. Incident
  descriptions are scrubbed: the client, its people, its products and the org's executives
  become "the client" and "a stakeholder". `check_incidents.py` refuses the names.

## Not derivable here

- **0 CI minutes in the trial**: GitHub Actions usage is not in git. It is quoted from
  studio's record (`6b04ffe`) and not reproduced.
- Token or wall-clock cost per session: not recorded anywhere (studio's answer).
- Review rounds per node for studio: reviews run inside `building` and leave no board state.
  Only PASS markers (one per node, last write) and commit messages ("review round N") exist.

## Added by paper-writer (2026-10-02, draft and peer review)

- `derived.py` → `derived.json`: arithmetic only over the JSON files here (shares, spans,
  counts the text states that no single key holds). No git. Deterministic.
- `integrate_split.py --repo <bare clone of studio>` → `integrate_split.json`: git-only,
  read-only, at studio's pin. When integrate.sh reached trunk (`0416e3d`, 2026-09-29T20:30
  -04:00); branch→trunk merges before/after it (22 / 108) and after it with the script's
  subject form (93, an upper bound: the form can be typed by hand); hand merges of trunk into
  a branch before/after (8 / 147); the 4 hand-resolved merges that are not hand trunk→branch
  merges, each before or after the script. Totals reconcile with `integrations.json`
  (130, 155, 53). Byte-identical on re-run.
