# The org's research inventory

research-scout, node `inventory` (plan 02), 2026-10-02. Read-only survey of every department's
**committed** `main`. Nothing was run; every number below is the source department's own,
**not reproduced here** unless a later reproducer note says so.

Sources read (department @ `main`):
studio `af5aaf2` · mir-triage `2599ceb` · copy-in-product-picture `48f062f` ·
product-in-picture `c0b095d` · product-in-video `fd56d29` · design-manufacture-interface
`8cc1238` · gateway `b355a06`.

The wider list of paper ideas (every department, including thin ones) is
[`paper-ideas.md`](paper-ideas.md). This file is the ranked shortlist of results that exist.

**How to read it.** *Measured* = the department ran it and recorded numbers. *Argued* =
a design decision or a plan with reasons but no measurement. *Readiness* 1-5: 1 = an idea,
2 = measured on private data only, 3 = measured and reproducible on public/synthetic data
with modest work, 4 = reproduced here, 5 = draft-ready. *Privacy*: what a paper would have
to withhold (never copy it here).

## Ranked shortlist

| # | Candidate | Dept | Evidence | Readiness | Novelty (honest) | Privacy | Venue type |
|---|---|---|---|---|---|---|---|
| 1 | **A one-person software org run by concurrent Claude lead sessions** (git feature graph, atomic claims, integrate gate, deploy-at-built, dated failure lessons, kits that bootstrap new departments) | studio (+ every dept) | measured: trial record, 1,355 commits / 351 merges in 5 days, 25 dated incident lessons; tooling with race tests | **3** | moderate: multi-agent SE is crowded, but a long-running, real, git-native, human-steered case study with incident data is rare | low: scrub Haki and Tracklib names; nothing private needed | SE experience report (ICSE-SEIP / FSE industry / an AIware or agents workshop), arXiv |
| 2 | **Stem sets: grouping a download by content, aligning, and auditing it against its master** (onset-xcorr + prominence link rule, master by spectral containment, coverage with a mastering model, DSP bleed, master-matched tiers) | mir-triage | measured on a small licensed library + synthetic tests | **3** | moderate: alignment and mix reverse-engineering exist; the "is this stem download complete and which file is the master" audit is not a standard task | medium: all real measurements on Tracklib-licensed audio; re-measure on Slakh2100 / MUSDB18 / MedleyDB | ISMIR LBD or full paper, DAFx, AES convention |
| 3 | **Phrase-aware cuts for sample-based production** (vocal phrases, `phrase_cut` penalty, pickup windows, pickup-shifted joins; tagger fallback without a vocal stem) | mir-triage | measured on **one** vocal track (+ tagger calibration on it) | **2** | moderate: anacrusis is known musicology; measuring how bar-aligned loop extraction cuts sung notes, and fixing it, is not in the loop/sample MIR literature we found | medium: licensed audio; re-measure on MUSDB18-HQ vocals | ISMIR LBD |
| 4 | **Vintage-ness as measurable descriptors** (hf slope knee, codec cliff, minimum-statistics hiss, common-mode wow line that names a 33 1/3 rpm disc) + a provenance-tagged taste profile | mir-triage | measured: estimators tested on synthesised audio (34 tests); calibrated by added hiss/wow on 4 real tracks; n=1 liked record | **2** | low-moderate: wow detection from programme material exists (Czyżewski et al.); the rotation-line test and the "profile with basis tags" framing are the new parts | medium: licensed audio; estimators reproducible on synthetic + public-domain transfers | DAFx / AES / ISMIR LBD |
| 5 | **Drawn-ink phone legibility vs flat-colour WCAG** for ad text | copy-in-product-picture | measured once (an evaluator FAIL on thin faces) | **2** | low-moderate: APCA already weights font weight; an as-rendered, downsampled p90 measure is a small, checkable note | none if redone with OFL fonts on synthetic backgrounds | CHI LBW / design-tooling workshop |
| 6 | **Classical layered decomposition of flat ad images** (rings, fades, render-and-compare font fit, edge matte, refuse-to-cut rule) | copy-in-product-picture | measured on 3 private PSD/export pairs + evaluator inputs | **2** | low: LayerD (ICCV 2025) and learned methods lead; ours is a classical, template-family-specific baseline | **heavy**: Haki designs; would need Crello or synthetic designs | workshop / arXiv tech report |
| 7 | **Benchmarking on a shared, drifting laptop**: a paired calibration workload per sample | copy-in-product-picture | measured: back-to-back runs of unchanged code differ +24-27% | 2 | low: Kalibera & Jones and others cover this | low (synthetic-v1 set exists) | blog / tech note, not a paper |
| 8 | Shot tags with calibrated abstention (CLIP zero-shot + pixel rules) | product-in-picture | measured on 168 private hand labels | 1-2 | low | **heavy** (catalogue) | not recommended |
| 9 | Swipe verdicts as a taste signal (CEO/COO) | org (copy, pip) | argued; no data yet | 1 | moderate if data ever exists | heavy (Haki items, people's votes) | later |

**Recommendation for the first paper: #1** (agentic org experience report). It is the only
candidate with a large, already-committed, non-private evidence base; the missing numbers
(node lead times, collision and review-round counts, incident rates) can be mined from the
committed `graph.yaml` histories and logs without running anyone's code or touching private
data. **Second: #2** (stem sets), because it can be re-measured end to end on public
multitrack datasets with the department's own tests as the method spec. #3 folds into #2 as a
section, or becomes an LBD once measured on more than one song.

---

## 1. A one-person software org run by concurrent Claude lead sessions

**Claim.** A single engineer can run several concurrent LLM "lead" sessions on one laptop as a
working software organisation, coordinated only through git (a feature DAG with `touches`
globs, atomic `mkdir` claims, one locked integration script, deploy-at-built), and its
failure modes are concrete, recurring and fixable by rules recorded in the repo.

**Evidence (measured unless noted).**
- Design: studio `claude-plans/06-multi-lead.md`, ADR `docs/decisions/0024-multi-lead-orchestration-and-rare-ci.md`;
  built in `16042df` (graph, M1), `df511e9` (claims and mutexes with race proofs, M2),
  live channel and pipeline board after.
- Trial record (`6b04ffe`, plan 06 "Trial record"): three leads, ~2 h, 2026-09-30; nodes
  merged in parallel with **no file, number or deploy collisions**; three coordination
  conflicts, each settled by the claim table; **0 CI minutes** used (all gates local); month
  estimate ~300 of 2,000 free minutes.
- Scale: studio 1,355 commits, 351 merges, 2026-09-28 → 10-02; 1,257 carry a Claude co-author
  line; lead sessions numbered to at least lead-13. The pattern was copied by kit into six more
  repos (mir-triage 130 commits, copy 144, pip 31, piv 30, dmi 5, gateway 25), all with the same
  `scripts/lead/` tooling (`claude-plans/handoffs/2026-10-02-*-kit/`).
- Incident data: 25 dated lessons in `.claude/skills/lead-playbook/SKILL.md` §Lessons, e.g. a
  Playwright run at default workers took load to 81 on 8 cores for 40 min; an in-place script
  rewrite killed a running deploy; an uncommitted migration in the main checkout nearly reached
  the live DB via the auto-deployer; every lead died at a lock screen and left claims; a
  regex spec filter matched the worktree's own name and ran the whole suite.
- Governance: the gateway (`gateway/steering.md`) relays direction but never approval
  (spend, deletion, publishing, the people gate) — a written authority split.
- Argued, not measured: speed-ups vs a single session, cost in tokens, quality vs review gates.

**Checked by the reproducer (2026-10-02, paper-1 branch, `papers/org-of-one/evidence/`).**
Reproduced: studio 1,355 commits / 351 merges / 1,257 Claude co-author lines; lead-1…13; the
per-repo commit counts. **Corrections:** the full `scripts/lead/` kit is in 6 repos (studio,
mir-triage, copy, piv, dmi, research-to-publication); pip and gateway have a playbook but no
tooling. The trial had **no blocking conflicts**, not "no collisions": 2 hand-resolved merges
and 1 lost board update in a 1.26 h window, and three leads overlapped for about a minute
(otherwise two). "0 CI minutes" can't be checked from git (quoted from the record). "25
lessons" is studio's; org-wide there are 61 dated lessons, 46 distinct.

**Missing.** Per-node lead time, review rounds and rework, collision/near-miss rates over the
whole history (minable from `graph.yaml` git history and merge commits); token/time cost;
any comparison baseline (single lead vs N leads on comparable nodes).

**Related work.** MetaGPT ([arXiv 2308.00352](https://arxiv.org/pdf/2308.00352v6)) and ChatDev
(role-play pipelines, benchmark tasks, not a live org);
[When Agents Coordinate (arXiv 2608.16801)](https://arxiv.org/abs/2608.16801) measures
coordination in 1,902 synthetic multi-agent coding runs;
[Mixed-method experience report on LLM MAS in SE (arXiv 2608.11965)](https://arxiv.org/abs/2608.11965);
[EvoGit (arXiv 2506.02049)](https://arxiv.org/pdf/2506.02049) uses git as the coordination
substrate; [LLM-MAS for SE survey (arXiv 2404.04834)](https://arxiv.org/pdf/2404.04834);
practitioner write-ups on worktree-parallel agents
([Mason 2026](https://mikemason.ca/writing/ai-coding-agents-jan-2026/)). Gap we would fill: a
longitudinal, real-product, single-human case study with an incident log and a human authority
model, not a benchmark.

**Privacy.** None needed. Scrub Haki/Tracklib/people names from examples; the user's own words
are quoted in the repos and would need the user's yes to quote.

**Readiness 3. Venue:** experience report (ICSE SEIP, FSE industry track) or an agents/AIware
workshop; arXiv preprint. **Recommend as paper 1.**

## 2. Stem sets: grouping, alignment and completeness audit of a multitrack download

**Claim.** The files of a stem download can be grouped, the master identified and every stem
aligned by content alone, and the places where the master holds a part no stem carries can be
found, with simple DSP and measured thresholds.

**Evidence** (mir-triage `docs/research-notes.md` "Stem sets", "Stem coverage", "Layer map,
bleed and tiers"; plan `claude-plans/05-stem-sets.md`; code `5292dd4`, `5824ebb`, `596a816`,
MP3 `cd75107`; tests `tests/test_stemsets.py` (32), `tests/test_coverage.py` (8), `tests/test_tiers.py`).
- Link rule measured on master–stem, stem–stem, unrelated and *hard negative* pairs (same
  record, different moments): onset r alone cannot separate them; **prominence** (peak minus
  best r ≥ 0.1 s away) can. Rule r ≥ 0.15, prominence ≥ 0.04; a drift "second look" fixed a
  0.1 % resampled stem and never fired on 78 negatives.
- Master by **spectral containment** (0.85 threshold), measured to beat "highest mean
  correlation", which picked a drum stem on a drum-dominated synthetic mix.
- Coverage: per-band median EQ + 2 s broadband gain as the mastering model; synthetic
  tilt + 4:1 compression flags nothing, an added part flags exactly its bars; one real gap
  verified by ear.
- MP3: sets group identically when the LAME/Info tag is present (decoder trims delay,
  offsets 0.00 ms); without it a 1105-sample delay is detected and explained.
- Limits stated: stems-only sets group poorly on real audio; thresholds from a handful of
  tracks.

**Missing.** Any public-data evaluation; a dataset of incomplete stem sets (constructible:
drop/mute a stem in Slakh2100 or MUSDB18, re-master the mix with random EQ/compression);
baselines (GCC-PHAT, chroma-DTW, a learned stem-retrieval embedding).

**Related work.** Mix reverse engineering: [Barchiesi & Reiss 2010, JAES](https://joshreiss.github.io/documents/2010/BarchiesiReiss-ReverseEngineeringofaMix.pdf);
[differentiable mix reverse engineering (2021)](http://eecs.qmul.ac.uk/~josh/documents/2021/10.0005622.pdf).
Stem retrieval/compatibility: [Zero-shot stem retrieval, arXiv 2411.19806](https://arxiv.org/abs/2411.19806),
[Stem-JEPA, arXiv 2408.02514](https://arxiv.org/html/2408.02514),
[Stembed, arXiv 2609.35672](https://arxiv.org/abs/2609.35672) (seen in search, not read).
Sample identification: [Riou et al. 2025, arXiv 2510.11507](https://arxiv.org/abs/2510.11507),
[ISMIR 2017 sample detection](https://archives.ismir.net/ismir2017/paper/000118.pdf).
Loops: [Unmixer, ISMIR 2019](https://archives.ismir.net/ismir2019/paper/000101.pdf),
[López-Serrano et al. 2016](https://www.audiolabs-erlangen.de/resources/MIR/2016-ISMIR-EMLoop).
Prominence is the correlation peak-to-sidelobe idea; cite it as such, not as new.

**Privacy.** Every real number is on Tracklib-licensed audio ("Clearance Required"): no audio,
no track names in a paper without the user's yes; re-measure on public sets
(Slakh2100 CC BY 4.0; MUSDB18-HQ and MedleyDB are research/non-commercial: check terms).

**Readiness 3. Venue:** ISMIR (LBD first, full paper with the public benchmark), DAFx or AES.

## 3. Phrase-aware cuts, pickup windows and pickup-shifted joins

**Claim.** Bar-aligned loop extraction routinely cuts sung notes because vocal phrases start
before the downbeat; a per-window `phrase_cut` penalty, pickup-shifted windows and joins that
move by whole 16ths fix most of it, and a general audio tagger is good enough to do this
without a vocal stem.

**Evidence** (mir-triage research notes "Vocals branch and phrase-aware cuts", "Vocal activity
without a vocal stem"; plans 12, 13; `49262a6`, `b5eb2b3`, `d958f48`; tests
`tests/test_vocals.py`, `tests/test_join_shift.py`, `tests/test_tagger*.py`). On one track:
27 phrases, none starts on a downbeat, 24 start 1-1.8 beats early; 78 % of master windows cut a
sung note; joins cutting a note in full arrangements 29/53 → 19/54; tagger vs stem per-beat
agreement 0.91, per-beat AUC 0.945, `phrase_cut` r 0.85 with the stem's; zero false positives on
five non-vocal inputs. By-ear verification pending.

**Missing.** More than one song (n=1 vocal, n=1 hard negative); public data (MUSDB18-HQ vocals
give ground-truth phrases); a listening test.

**Related work.** Loop/sample MIR above; note segmentation
([phoneme-informed, NLP4MusA 2021](https://aclanthology.org/2021.nlp4musa-1.4.pdf));
PANNs (Kong et al. 2020) as the tagger; mashup compatibility
([Neural Loop Combiner, ISMIR 2020](https://arxiv.org/pdf/2008.02011)). We found no paper
measuring phrase damage from grid-aligned slicing.

**Privacy.** Licensed audio (as #2). **Readiness 2. Venue:** ISMIR LBD; or a section of #2.

## 4. Vintage descriptors and a provenance-tagged taste profile

**Claim.** "Vintage" in a mix is measurable (high-frequency slope above a knee, codec cliff,
hiss floor, a common-mode wow line at a disc's rotation rate), and an aesthetic brief can be held
as a machine-readable profile whose every range is tagged with its basis (probe, literature,
prior, ears).

**Evidence.** mir-triage `claude-plans/22-taste-descriptors.md`, `docs/cafe-beats/00-05`,
`src/mir_triage/core/taste.py`, `tests/test_taste.py` (34 test functions on synthesised audio: BS.1770
and EBU 3341/3342 tables, wow at 0.5 Hz, disc rotation, vibrato not wow); merge `e63cc4f`.
Calibration with added hiss and wow on four real tracks; the liked record shows a clear wow line
at the 33 1/3 rpm rotation rate and a much steeper hf slope than the others (figures measured on
licensed audio: withheld here until mir-triage says they may be quoted). Limits measured: a
3-5 cent wow floor on dense mixes; hiss is a lower bound when the band never goes quiet.

**Missing.** More than one liked record; any listener data; public test material
(public-domain 78/LP transfers, e.g. archive.org, with synthetic degradations as ground truth).

**Related work.** [Czyżewski et al., wow detection from spectral processing](https://www.semanticscholar.org/paper/Wow-Detection-and-Compensation-Employing-Spectral-Czy%C5%BCewski-Dziubi%C5%84ski/b91936d53882b33e073ffd2b6712a73fdc36de55);
[parasitic FM detection](https://www.researchgate.net/publication/230585000_Methods_for_Detection_and_Removal_of_Parasitic_Frequency_Modulation_in_Audio_Recordings);
wow/flutter standards (AES6-2008, IEC 386). **Readiness 2. Venue:** DAFx / AES / ISMIR LBD.

## 5. Phone legibility measured on drawn ink

**Claim.** Flat-colour WCAG contrast passes accent text that fails once a thin face is
antialiased down to phone width; a p90 ink-luminance contrast at 360 px catches it.

**Evidence.** copy-in-product-picture `docs/contracts/variant.md` (legibility rule, 390 → 360 px),
`.claude/agent-memory/composer-dev/project_phone_legibility_bar.md` (evaluator FAIL: 28 px
sublines at weight 300-500 failed the bar; figures measured on a Haki ad, withheld); merges `35c948d`, `fbd7bed`. Measured once.

**Missing.** A systematic sweep (fonts × weights × sizes × backgrounds), a human legibility
check, comparison with APCA. All doable on OFL fonts and synthetic backgrounds.

**Related work.** [APCA](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html),
[WCAG 3 text contrast discussion](https://github.com/w3c/silver/issues/285).
**Privacy:** none if redone synthetically. **Readiness 2. Venue:** CHI LBW / workshop note.

## 6. Classical layered decomposition of flat ad images

**Claim.** For one template family, a flat ad can be decomposed into an editable layer
template (rings, fade, live text with font/size/tracking, hero matte) with classical methods
on CPU, and should refuse to cut when product/ground contrast is too low.

**Evidence.** copy-in-product-picture `docs/research/decompose.md` (`e8c1848`, `e31c634`,
`fb5ad0d`): measured against 3 PSD ground truths plus crop/rescale variants and evaluator
inputs; three review rounds recorded. **All on Haki's private designs: numbers withheld here.**
**Missing:** public data (Crello / synthetic designs), comparison with LayerD.
**Related work.** [LayerD, ICCV 2025](https://arxiv.org/abs/2509.25134).
**Readiness 2, novelty low. Privacy heavy.** Not a first paper.

## 7. Benchmarking on a drifting shared laptop

copy-in-product-picture `docs/research/perf-baseline.md`, `docs/contracts/bench.md` (`0e331af`):
a ~23 ms calibration workload timed after every sample, gate on the normalised p50, because
back-to-back runs drifted +24-27 %. Known territory
([Kalibera & Jones 2013](https://kar.kent.ac.uk/33611/45/p63-kaliber.pdf)). Engineering; useful
as a method section inside #1, not a paper.

## 8-9. Thin or private

- **Shot tags with abstention** (product-in-picture `docs/research/shot-tags.md`, `fdc1717`):
  CLIP zero-shot + pixel rules, per-class abstention calibrated to dev precision ≥ 0.9; labels
  are on Haki's catalogue. Low novelty, heavy privacy.
- **Haki swipe taste loop** (copy `claude-plans/07-swipe.md`, `docs/contracts/decisions.md`):
  CEO/COO verdicts on factorised variant axes, later argued with A/B results. No data yet.

## Surveyed, engineering only (no paper)

studio plan 11 (upload hot path: analysis 591 s / render 454 s / previews ~20 s fixed cost —
an engineering report), studio ADRs 0001-0043 (stack, loudness-matched previews, self-healing
jobs, deploy drain), mir-triage FL hand-off (ACID/smpl chunks), Whisper chop words (plan 19;
packing phrases into 28 s windows, hallucination guards — close to
[Jam-ALT](https://arxiv.org/abs/2311.13987) / [LyricWhiz](https://arxiv.org/html/2306.17103v4)
territory), ideas engine (argued; by-ear pending), product-in-video decomposition survey
(`a6a6d92`, synthetic clip, tool/licence survey), product-in-picture query graph (argued, 10
synthetic tests), design-manufacture-interface (plan only, no results yet).

## Questions for department leads

1. **mir-triage:** (a) May we quote numbers measured on the Tracklib library (no audio, no
   names) in a draft, or must every number be re-measured on public data? (b) Are the by-ear
   checks for phrase cuts and pickup joins done anywhere not yet committed? (c) Would you accept
   a reproduction of `stemsets`/`coverage` on Slakh2100/MUSDB18 in a throwaway clone, and which
   commit should we pin?
2. **studio:** (a) Is `graph.yaml`'s git history the complete record of node states, or did
   some state live only in `.worktrees/.state/` (claims, pass markers)? (b) Any record of
   token/time cost per lead session? (c) Is the trial in plan 06 the only measured multi-lead
   trial?
3. **copy-in-product-picture:** would you accept the legibility rule being re-measured on OFL
   fonts and synthetic backgrounds (no Haki pixels) for a short note?
4. **The user (via the lead):** which of #1 / #2 becomes paper 1; whether the user's quoted
   directives may appear verbatim in #1; authorship.

## Answers from department leads (2026-10-02)

**mir-triage** (mir-triage-lead-2, answering for lead-1 too):
- (a) **Keep withholding Tracklib numbers; re-measure on public data** (Slakh2100, MUSDB18).
  Quoting measurements of licensed "Clearance Required" material is the user's call and has
  not been asked; their docs also name tracks. Tracklib figures only with the user's explicit
  yes, and then aggregated and anonymised. mir-triage passed the question to gateway-1.
- (b) **No by-ear verdicts exist.** The listening checks for phrase cuts, pickup windows,
  pickup joins and chops are all still open. Those results are *measured, unchecked by ear*
  and may not be stated as heard or verified.
- (c) Pin mir-triage `main` **`c2c9a68`** for stemsets + coverage (includes the MP3 stem-set
  notes `2927bd2`; WAV grouping unchanged). If the paper covers no-master or submix
  downloads, pin the commit after their plan 24 (fix-no-master-submix) merges; lead-1 will
  give the SHA.
  **Update (mir-triage-lead-1, 2026-10-02): plan 24 merged at `2a91696`. Pin `2a91696` for
  the stem-set paper** (a full mix holding a part no member has becomes the master by content;
  a bounce of several members stays in its set flagged `mix`, never summed). Public data only.

**studio** (lead-9):
- (a) `graph.yaml` history (320 commits, all branches) has node **states** only. Claims,
  number reservations, locks and PASS markers (78) live in studio's gitignored
  `.worktrees/.state/`; claims are deleted on release, so who-held-what history is gone except
  in integrate commit messages and the In-flight table in studio's `claude-plans/01-review-app.md`.
- (b) **No token or wall-clock cost per lead session is recorded.** Transcripts (not in git)
  may hold usage, unverified.
- (c) Deploy history: an uncommitted live-history log (116 lines) and an autodeploy log on
  this Mac; `live.json` is current state only.
- (d) ui-reviewer reports are not committed; findings are in transcripts, In-flight rows and
  plan 01's backlog, evidence in uncommitted state dirs.
- (e) Plan 06 is the only recorded *trial*. 2026-09-30 to 10-02 ran up to five studio leads at
  once in production (lead-1 … lead-13): observational data, incidents in the lead-playbook
  lessons.

**Consequences for candidate #1.** The paper rests on committed history (board states, merge
and integrate commits, plans, lessons) and is framed as an observational case study plus one
small trial, not a controlled experiment. Cost/speed-up claims are out unless measured anew.
Studio's uncommitted state (PASS markers, deploy logs) needs studio's agreement to read as
evidence. Session transcripts and reviewer shots may hold Haki details or licensed track
names, so they need the user's yes first.

**studio's agreement** (lead-9, 2026-10-02): if the user picks #1, we may read studio's
`.worktrees/.state/` (claims, resources, locks, pass, live-history.log) and
`~/.sample-staging/logs/autodeploy.log` **read-only** as evidence. They hold session names,
node ids, SHAs, times and paths, and no client data. Rules: copy only aggregates or quoted
lines into this repo; never the `shots/` folder; never create or delete anything in `locks/`
(live mutexes). Transcripts and shots remain the user's call.
