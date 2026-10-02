---
name: research-to-paper
description: research-to-publication's rules for turning the org's research into papers - the inventory, novelty and related-work checks, evidence tracing (every number to a commit, test, reproduced measurement or citation), reproduction in throwaway copies, privacy and licensing of data in figures, open-source typesetting with figures generated from scripts, and the never-submit-without-the-user rule. Load before inventorying, reproducing, writing or reviewing.
---

# research-to-paper

## Where the research is (read-only, committed files)
- mir-triage: `docs/research-notes.md`, `claude-plans/` (steps, decisions with alternatives),
  `docs/cafe-beats/` (when merged), evaluator findings; the engine's tests.
- studio: `docs/spec.md`, `docs/architecture.md`, `docs/decisions/` (ADRs), `claude-plans/`
  (incl. plan 11's hot-path measurements), lessons in its lead playbook.
- copy-in-product-picture, product-in-picture, product-in-video: `docs/research/`, plans,
  contracts (`docs/contracts/decisions.md`), evaluator reports.
- design-manufacture-interface: plans and the spec model.
- The Haki swipe verdicts (votes) are data: aggregate counts only, with the user's yes.

## Novelty and related work
A claim is a paper only if it is new or newly well measured. Search open sources (arXiv,
Semantic Scholar, ACL/ISMIR/CVPR proceedings, project docs) and record what exists; say plainly
when the work is an engineering report rather than research.

## Evidence
Every number in a paper has a source: the commit and file it came from, or this department's
reproduction (command, environment, seed, result). A number not reproduced here is labelled.

## Reproduction
Only in a throwaway copy of the source repo at the cited commit, with a scratch state dir and
synthetic or public inputs; never in another department's checkout, never against live data;
heavy runs under the shared lock.

## Privacy and licences
No Haki private data, Devin's media, licensed audio or personal data in a paper or this repo
without the user's (and Devin's) yes. Figures use synthetic or public data where possible.
Cite every dataset and model with its licence.

## Typesetting
Open source only, pinned in plan 01 (e.g. a LaTeX engine distributed as a single binary, or
pandoc; verify an Intel-Mac build without a source compile). The paper builds from `main.tex`,
`refs.bib` and figure scripts; PDFs and figures are build output, never committed.

## Never
Submit, post, upload or publish anything, or share a draft outside the org, without the user.
