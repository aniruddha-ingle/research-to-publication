# Paper ideas from the problems the org is solving

research-scout, 2026-10-02, for the user's "task 1. curate all possible research paper ideas
from the problems we are solving across the organisation" (relayed by gateway-1).

Companion to [`inventory.md`](inventory.md) (the ranked shortlist with full evidence and
related work). This file is wider: every department plus the org itself, thin ideas included,
with how thin they are. Ranked by **the strength of today's committed evidence**, not by how
exciting the idea is. Sources: each department's committed `main` (studio `af5aaf2`,
mir-triage `2599ceb`, copy-in-product-picture `48f062f`, product-in-picture `c0b095d`,
product-in-video `fd56d29`, design-manufacture-interface `8cc1238`, gateway `b355a06`).
No number here was reproduced by this department yet.

**Keys.** Evidence: *measured* (numbers recorded), *argued* (design reasons only), *none yet*.
Haki data: **none** (paper needs nothing of Haki's), **derived** (only numbers or findings that
came from Haki material, which must be re-measured on public or synthetic data or withheld),
**heavy** (the work is about Haki's own designs, catalogue, ads or votes). Haki data is never
copied here in any case. Effort: **S** ≈ a week, **M** ≈ 2-4 weeks, **L** ≈ 1-3 months of
agent + reviewer time, with the work named.

## Top 5

| # | Working title | Dept | Evidence today | Haki data | Effort | Venue type |
|---|---|---|---|---|---|---|
| 1 | *An org of one: running a software company with concurrent LLM lead sessions coordinated through git* | studio + all | measured: 1,355 commits / 351 merges in 5 days, a 3-lead trial with 0 collisions and 0 CI minutes, 25 dated incident lessons, 7 repos built from kits | none | M (mine git/graph history; write) | SE experience report / agents workshop / arXiv |
| 2 | *Is this stem download complete? Grouping, aligning and auditing multitrack sets against their master* | mir-triage | measured on a small licensed library + 40 synthetic tests | none (Tracklib audio instead: re-measure on public sets) | M (public benchmark from Slakh2100/MUSDB18; baselines) | ISMIR / DAFx / AES |
| 3 | *How LLM agent teams break a shared laptop: an incident study* | studio + all | measured: 25 dated incidents with causes and fixes | none | S-M (code the incidents; cross-check in git) | SE / ops workshop, arXiv |
| 4 | *Don't cut the singer: phrase-aware loop extraction and pickup-shifted joins* | mir-triage | measured on 1 vocal track | none (licensed audio: re-measure on MUSDB18-HQ) | M (phrase ground truth from public vocal stems; listening check) | ISMIR LBD |
| 5 | *Measuring "vintage": spectral, noise and disc-rotation descriptors for a taste profile* | mir-triage | measured: 34 synthetic-audio tests, calibration on 4 tracks, n=1 liked record | none (licensed audio: use public-domain transfers) | M (public test set with synthetic degradations) | DAFx / AES / ISMIR LBD |

Recommendation stands from the inventory: **#1 first** (largest non-private evidence base),
**#2 second**; #3 can be a section of #1 or a short companion; #4 can be a section of #2.

---

## Ranked list

### 1. An org of one: a software company of concurrent LLM lead sessions (org + studio)
- **Problem.** One engineer with a day job wants several products built at once by LLM
  sessions that don't collide, don't wait on him, spend nothing and stay steerable.
- **Contribution.** A git-native coordination design (feature DAG with `touches` globs,
  atomic `mkdir` claims, one locked integrate gate, deploy-at-built live channel, rare CI) and a
  longitudinal record of running it on a real product, then cloning it into six departments.
- **Evidence today.** studio `claude-plans/06-multi-lead.md`, ADR 0024; built `16042df`,
  `df511e9`; trial record `6b04ffe` (3 leads, ~2 h, no file/number/deploy collisions, 3 claim
  conflicts settled by the table, 0 CI minutes). Volume: studio 1,355 commits, 351 merges,
  2026-09-28 → 10-02, 1,257 with a Claude co-author line; leads numbered to lead-13; kits in
  `claude-plans/handoffs/2026-10-02-*` reproduced the pattern in mir-triage, copy, pip, piv,
  dmi, gateway and this repo.
- **Missing.** Per-node lead time, review rounds, rework and collision rates (minable from
  `graph.yaml` history); cost in tokens/hours; a baseline (1 lead vs N). Is `.worktrees/.state/`
  (claims, pass markers) lost? Ask studio.
- **Closest prior work.** [MetaGPT](https://arxiv.org/pdf/2308.00352v6), ChatDev (role
  pipelines on benchmark tasks); [When Agents Coordinate, arXiv 2608.16801](https://arxiv.org/abs/2608.16801)
  (1,902 synthetic runs); [EvoGit, arXiv 2506.02049](https://arxiv.org/pdf/2506.02049) (git as
  substrate); [MAS-in-SE experience report, arXiv 2608.11965](https://arxiv.org/abs/2608.11965);
  [LLM-MAS for SE survey](https://arxiv.org/pdf/2404.04834).
- **Venue.** ICSE SEIP / FSE industry, an agents or AIware workshop; arXiv.
- **Haki data.** none. **Effort.** M: a mining script over 7 repos' committed history, 3-4
  figures, a write-up; no code of theirs run.

### 2. Is this stem download complete? (mir-triage)
- **Problem.** Sample-clearance downloads ship a master and stems with unreliable names and
  sometimes missing parts; producers need to know which file is the master, how stems align,
  and where the stems don't add up.
- **Contribution.** Content-only grouping with a **prominence** link rule tested on hard
  negatives, master by spectral containment, sub-frame offsets with drift check, a coverage
  measure that models mastering (per-band median EQ + slow broadband gain), DSP bleed, and
  master-matched tiers.
- **Evidence today.** `docs/research-notes.md` (Stem sets, coverage, bleed, tiers),
  `claude-plans/05-stem-sets.md`; `5292dd4`, `5824ebb`, `596a816`, `cd75107`;
  `tests/test_stemsets.py` (32), `tests/test_coverage.py` (8). Measured on Tracklib material
  (5 master–stem, 10 stem–stem, 21 unrelated, 36 hard-negative pairs; 78 negatives never
  triggered the drift look) and synthetic EQ/compression cases.
- **Missing.** Public evaluation; a dataset of incomplete sets; baselines (GCC-PHAT,
  chroma-DTW, a learned stem embedding).
- **Closest prior work.** [Barchiesi & Reiss 2010](https://joshreiss.github.io/documents/2010/BarchiesiReiss-ReverseEngineeringofaMix.pdf),
  [differentiable mix reverse engineering](http://eecs.qmul.ac.uk/~josh/documents/2021/10.0005622.pdf),
  [zero-shot stem retrieval](https://arxiv.org/abs/2411.19806), [Stem-JEPA](https://arxiv.org/html/2408.02514),
  [multi-track contrastive sample ID](https://arxiv.org/abs/2510.11507).
- **Venue.** ISMIR (LBD, then full with the benchmark), DAFx, AES.
- **Haki data.** none (licensed Tracklib audio is the constraint). **Effort.** M: build
  "incomplete set" cases from Slakh2100 (CC BY 4.0) with random mastering; run the
  department's code at a pinned commit in a throwaway clone.

### 3. How LLM agent teams break a shared laptop: an incident study (org)
- **Problem.** Many agent sessions on one machine fail in ways single-session coding never
  shows: resource starvation, lock-holding hangs, sessions dying silently, edits in the wrong
  checkout.
- **Contribution.** A coded taxonomy of real incidents with cause, blast radius, detection and
  the rule that fixed it.
- **Evidence today.** studio `.claude/skills/lead-playbook/SKILL.md` §Lessons (25 dated
  entries), e.g. load 81 on 8 cores for 40 min from one test run; a deploy killed by an
  in-place script rewrite; an uncommitted migration in the main checkout nearly applied to
  live; every lead dying at a lock screen with claims held; a spec regex matching the
  worktree's name. Similar lessons in mir-triage and copy playbooks (load cap, heavy-test lock).
- **Missing.** Each incident cross-checked against commits; frequency and time-to-fix; the
  other departments' incidents coded the same way.
- **Closest prior work.** Postmortem/incident-analysis literature in SRE; agent failure
  analyses in the multi-agent SE papers above. Likely new as a real-hardware agent incident set.
- **Venue.** workshop or a section of #1. **Haki data.** none. **Effort.** S-M.

### 4. Don't cut the singer: phrase-aware loop extraction (mir-triage)
- **Problem.** Bar-aligned slicing cuts sung notes because vocal phrases start before the
  downbeat.
- **Contribution.** `phrase_cut` penalty, pickup windows that still loop on the grid,
  joins that move by whole 16ths, and a tagger fallback (PANNs) when there's no vocal stem.
- **Evidence today.** research notes "Vocals branch…", "Vocal activity without a vocal stem";
  `49262a6`, `b5eb2b3`, `d958f48`; tests `test_vocals.py` (15), `test_join_shift.py` (7). One
  track: 27 phrases, none on a downbeat; joins cutting a note 29/53 → 19/54; tagger per-beat
  AUC 0.945, `phrase_cut` r 0.85 vs the stem. **Thin: n = 1 song, by-ear checks pending.**
- **Missing.** MUSDB18-HQ / MedleyDB vocals as ground truth; a small listening test.
- **Closest prior work.** [Unmixer](https://archives.ismir.net/ismir2019/paper/000101.pdf),
  [Neural Loop Combiner](https://arxiv.org/pdf/2008.02011), [phoneme-informed note
  segmentation](https://aclanthology.org/2021.nlp4musa-1.4.pdf), PANNs (Kong et al. 2020).
- **Venue.** ISMIR LBD or a section of #2. **Haki data.** none. **Effort.** M.

### 5. Measuring "vintage" (mir-triage)
- **Problem.** An aesthetic brief ("historic vintage vibes … a Brooklyn cafe") has to become
  something a beat generator can be checked against.
- **Contribution.** Pure-DSP descriptors (hf slope + knee, codec cliff, minimum-statistics
  hiss, consensus wow with a line test that names a disc's rotation rate, self-calibrated
  clicks) and a profile where every range carries its basis (probe / literature / prior / ears).
- **Evidence today.** `claude-plans/22-taste-descriptors.md`, `docs/cafe-beats/00-05`,
  `core/taste.py`, `tests/test_taste.py` (34 test functions, synthesised audio); merge `e63cc4f`; hiss and wow
  calibration by addition on 4 tracks; measured floors stated. **Thin on taste: one liked record.**
- **Missing.** Public-domain transfers with synthetic degradations as ground truth; any
  listener ratings.
- **Closest prior work.** [Czyżewski et al. wow detection](https://www.semanticscholar.org/paper/Wow-Detection-and-Compensation-Employing-Spectral-Czy%C5%BCewski-Dziubi%C5%84ski/b91936d53882b33e073ffd2b6712a73fdc36de55),
  [parasitic FM detection](https://www.researchgate.net/publication/230585000_Methods_for_Detection_and_Removal_of_Parasitic_Frequency_Modulation_in_Audio_Recordings).
- **Venue.** DAFx / AES / ISMIR LBD. **Haki data.** none. **Effort.** M.

### 6. Direction is not approval: governing a human-steered agent org (gateway + all)
- **Problem.** When agents relay a human's wishes to other agents, which authority travels?
- **Contribution.** A written split: a relay carries goals, priorities and deadlines, never
  approval for spend, deletion, publishing or what named people see; plus gates (evaluator
  PASS as the COO gate) and the record of how it was applied.
- **Evidence today.** `gateway/steering.md` (dated directives, verbatim), the org and
  department `CLAUDE.md` files, copy `7b2608f`, `e7082cd`, piv `f22e560`. **Argued**, with a
  few recorded applications; no measured outcome.
- **Missing.** Cases where the rule was tested (a relayed ask refused, escalated); classifier
  denials recorded in studio lessons are a start.
- **Closest prior work.** Human-in-the-loop agent oversight, delegation and permissioning
  literature (to search properly).
- **Venue.** agents/AI-governance workshop; or a section of #1. **Haki data.** none.
  **Effort.** S as a section, M as its own paper.

### 7. Deploy at "built": a live channel for one user with agent builders (studio)
- **Problem.** The user wants features on his phone as soon as they're built, not after review.
- **Contribution.** `live = main + every eligible built node`, quiet window, verified backup,
  migration only via main, one-command rollback, an auto-deployer, and a drain rule for long
  jobs.
- **Evidence today.** plan 06 §10, ADRs 0026, 0042, 0023; plan 11 §1 (a deploy killed an
  analysis run; healed in 3 min by `retry_stalled`). Measured incidents, no aggregate stats.
- **Missing.** Deploy count, rollback count, time-from-built-to-phone from `live.json` history
  (not in git; ask studio).
- **Closest prior work.** continuous deployment / trunk-based development literature.
- **Venue.** section of #1. **Haki data.** none. **Effort.** S.

### 8. Departments from kits: bootstrapping new agent teams (studio + all)
- **Problem.** How fast can a new department reach useful work when it starts from another
  department's kit (agents, skills, board, tooling)?
- **Evidence today.** studio `claude-plans/handoffs/2026-10-02-*` (kits for mir research, pip,
  piv, dmi), the receiving repos' first commits (copy 144 commits on its first day, pip 31,
  piv 30, dmi 5). **Thin: counts only, no outcome measure.**
- **Missing.** Time to first merged node per department; what each kit changed.
- **Venue.** section of #1. **Haki data.** none. **Effort.** S.

### 9. Drawn-ink phone legibility vs flat-colour WCAG (copy-in-product-picture)
- **Problem.** Thin accent type passes flat-colour contrast checks but is unreadable on a phone.
- **Contribution.** Measure the antialiased glyph pixels at 360 px wide (p90 vs local median,
  4.5:1) and lift colour in OKLCH until it passes.
- **Evidence today.** `docs/contracts/variant.md` (legibility), composer-dev memory
  `project_phone_legibility_bar.md`; `35c948d`, `fbd7bed`. One evaluator FAIL with numbers.
  **Thin.**
- **Missing.** A sweep over OFL fonts × weights × sizes × backgrounds; APCA comparison; a
  small human check.
- **Closest prior work.** [APCA](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html),
  [WCAG 3 text contrast](https://github.com/w3c/silver/issues/285).
- **Venue.** CHI LBW / design-tools workshop. **Haki data.** none if redone synthetically
  (the original finding is derived). **Effort.** S-M.

### 10. Reviewer agents that never edit: do separate evaluators catch real defects? (org)
- **Problem.** Every department gates merges on a reviewer agent (ui-reviewer,
  creative-evaluator, mir-evaluator, video-evaluator, factory-reviewer, peer-reviewer).
- **Evidence today.** studio lessons (UI reviews took 3-4 rounds for one feature, later
  "one round, Blocker/Major only"); copy's decompose doc records three evaluator rounds with
  the defects found; mir-triage plan 22 "evaluator round 1/2". **Thin and scattered**; reviewer
  reports are mostly outside git.
- **Missing.** A count of findings by severity and whether each was a real defect.
- **Venue.** section of #1, or SE workshop. **Haki data.** derived (copy's findings are about
  Haki ads). **Effort.** M.

### 11. Benchmarking on a drifting shared laptop (copy-in-product-picture)
- **Evidence.** `docs/research/perf-baseline.md`, `docs/contracts/bench.md` (`0e331af`):
  back-to-back runs of unchanged code differ +24-27 %; a ~23 ms calibration workload per sample
  normalises it. Measured.
- **Prior work.** [Kalibera & Jones](https://kar.kent.ac.uk/33611/45/p63-kaliber.pdf). Known;
  **engineering**. Venue: a method note inside #1. **Haki data.** derived (haki-v1 specs; a
  synthetic-v1 set exists). **Effort.** S.

### 12. Classical layered decomposition of flat ads (copy-in-product-picture)
- **Problem.** Turn a flat ad back into an editable template.
- **Evidence.** `docs/research/decompose.md` (`e8c1848`, `e31c634`, `fb5ad0d`): measured
  against 3 PSD ground truths, crops, rescales and evaluator inputs; a refuse-to-cut rule for
  low contrast. All on Haki's designs (numbers withheld).
- **Missing.** Public data (Crello or generated designs), a LayerD comparison.
- **Prior work.** [LayerD, ICCV 2025](https://arxiv.org/abs/2509.25134) — stronger, learned.
- **Venue.** workshop / tech report. **Haki data.** heavy. **Effort.** L (new data).

### 13. Shot tags with calibrated abstention (product-in-picture)
- **Evidence.** `docs/research/shot-tags.md` (`fdc1717`): CLIP zero-shot prompt ensembles +
  pixel rules as log-odds, per-class abstention set for dev precision ≥ 0.9, held-out test on
  other products; 168 hand labels on Haki's catalogue.
- **Prior work.** CLIP zero-shot classification and selective prediction. Low novelty.
- **Venue.** not recommended alone. **Haki data.** heavy. **Effort.** M (public product
  photos would be needed).

### 14. No LLM per ad: compiling a typed request into one render plan (product-in-picture)
- **Problem.** The CEO types a request; thousands of ads must follow without an LLM per ad.
- **Evidence.** `docs/graph/README.md`, `schema.md` (`9624f61`): rules, then local CLIP text
  match, then "unresolved"; 2-40 ms per query; 10 synthetic tests. **Argued + a sketch.**
- **Missing.** A query set with judged outcomes.
- **Prior work.** semantic parsing to plans; retrieval-augmented generation (to search).
- **Venue.** workshop. **Haki data.** heavy for the real graph; derived for method. **Effort.** L.

### 15. Product features as ad content: page text + CLIP evidence (product-in-picture)
- **Evidence.** `docs/features/README.md`, `taxonomy.yaml`: per-category lexicon over product
  page text, CLIP prompts to find the photo that shows each feature. **Argued.**
- **Haki data.** heavy. **Effort.** L. Not a near-term paper.

### 16. Decomposing video ads into a timeline on CPU (product-in-video)
- **Evidence.** `docs/research/video-decompose.md` (`a6a6d92`): synthetic 8 s clip; cut
  detection exact on hard cuts, dissolve missed; OCR timing; tracker IoU; SAM 2.1 encoder cost;
  a PySceneDetect crash found; licence screen (AGPL YOLO out). **A survey**, measured on
  synthetic data only.
- **Venue.** blog / tech note. **Haki data.** none. **Effort.** M to make it a benchmark.

### 17. Silent video ads from stills (product-in-video)
- **Evidence.** `claude-plans/01-phase1-swipe-video-samples.md`: plan only, renders in flight.
  **None yet.** **Haki data.** heavy. Revisit when results land.

### 18. Tech packs that need no revisions: completeness checks mined from sample rounds (design-manufacture-interface)
- **Problem.** A first factory sample came back needing five revisions, each a field a
  complete tech pack would have stated.
- **Contribution (planned).** A spec model, standard headwear checks plus checks derived
  from past revision items, and a gap report; the test is whether the pack would have pre-empted
  every revision.
- **Evidence.** `claude-plans/01-haki-hat-poc.md` (draft); `8cc1238` (spec contract
  building). **None yet**; n = 1 product.
- **Prior work.** industry tech-pack guides; a [patent on CV-generated tech packs](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12439986).
  Little academic work found: possibly a real gap.
- **Venue.** fashion-tech / HCI workshop. **Haki data.** heavy (decks, measurements).
  **Effort.** L, and needs more products or a public tech-pack corpus.

### 19. The swipe taste loop: executive verdicts as preference labels (copy, pip, org)
- **Problem.** CEO and COO swipe on items from every department; can those verdicts, on
  factorised variant axes (style, type set, colourway, copy, product), predict what they keep
  and later what wins A/B tests?
- **Evidence.** copy `claude-plans/07-swipe.md`, `docs/contracts/decisions.md` (v2 +
  amendments: stable item ids, append-only verdicts, notes). **No data yet.**
- **Prior work.** [Creative4U, arXiv 2508.12628](https://arxiv.org/pdf/2508.12628),
  [ad creative ranking, arXiv 2008.07467](https://arxiv.org/pdf/2008.07467), conjoint analysis,
  dueling bandits.
- **Venue.** RecSys/KDD workshop later. **Haki data.** heavy (items, votes; aggregate counts
  only with the user's and Devin's yes). **Effort.** L, after months of votes.

### 20. Words for vocal chops on CPU (mir-triage)
- **Evidence.** plan 19, research notes "What a vocal chop says" (`5b2dcce`): packing phrases
  into ≤ 28 s windows (4× fewer encoder calls), word-to-chop assignment by word end,
  hallucination guards (compression ratio > 3.0), lyric/phonetic/sound kinds; 49/50 chops
  stable vs the experiment. n = 1 song, correctness unchecked by ear.
- **Prior work.** [Jam-ALT](https://arxiv.org/abs/2311.13987), [LyricWhiz](https://arxiv.org/html/2306.17103v4),
  [separation + Whisper ALT](https://arxiv.org/abs/2506.15514). **Engineering**; LBD at most.
- **Haki data.** none. **Effort.** M (Jam-ALT/JamendoLyrics evaluation).

### 21. Arranged ideas from stems: purist sketches with recipes (mir-triage)
- **Evidence.** plan 11, research notes "Ideas engine" and FX tier (step 16): role templates,
  25-cent conform rule, recipes that re-render bit-exact, stems that sum. **Argued**; by-ear and
  ratings pending (`scripts/fit_weights.py` exists, no ratings committed).
- **Prior work.** AutoMashUpper (Davies et al. 2014), [Neural Loop Combiner](https://arxiv.org/pdf/2008.02011),
  [stem compatibility for mashups](https://arxiv.org/pdf/2103.14208).
- **Haki data.** none. **Effort.** L (needs a listening study).

### 22. Review on a phone: card-stack audio review with loudness-matched previews (studio)
- **Evidence.** ADRs 0012 (static gain `min(−16 − L, −1 − TP, +6)` dB, no compression),
  0014 (card stack, keep/skip/love), the ratings tables. **Argued**; no user study.
- **Prior work.** streaming loudness normalisation; swipe-based relevance feedback. Known.
- **Haki data.** none. **Effort.** M (needs a study). Engineering today.

### 23. The upload hot path (studio)
- **Evidence.** plan 11 §1: 292 s of audio → ~30 min machine time (analysis 591 s, render 454 s,
  previews ~20 s fixed cost each). **Engineering report**, not research.

### 24. Docs as code as shared memory for humans and agents (studio)
- **Evidence.** plan 02 (generated data model/API/jobs docs, ADRs, drift checks in CI); a
  lesson where the health check found a backup a doc promised but nobody built. **Argued +
  one incident.** A section of #1.

---

## What I would send to the leads
Same questions as in `inventory.md` §Questions, plus:
- **studio:** is `live.json` history kept anywhere (for #7)? Are reviewer reports kept (for #10)?
- **design-manufacture-interface:** once `poc-hat-package` runs, will the "pre-empts all five
  revisions" result be recorded as a measurement (for #18)?
- **copy / pip:** will the swipe decisions log record the variant axes per item, so verdicts can
  later be analysed per axis without exposing the items (for #19)?
