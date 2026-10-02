# 01 · Typesetting (research-lead-1, 2026-10-02)

Node `typesetting`, gate light. Pick and pin open-source typesetting that runs on this Intel
Mac without a source build; a hello-world paper that builds from main.tex + refs.bib + one
figure script.

## Decision
Pin TeX Live 2022 (TinyTeX, already installed, prebuilt) + latexmk + bibtex/natbib; figures
from uv scripts (Python 3.11, pinned deps, wheels only). Full record and alternatives:
`docs/typesetting.md`.

## Done
- `papers/_template/`: `main.tex`, `refs.bib`, `figures/hello.py`, `Makefile`
  (`make`, `make figures`, `make check`, `make clean`).
- Proven: clean build in ~3 s, 2 pages, zero LaTeX warnings, citation resolved; the figure
  regenerates byte-identically.

## Follow-ups
- When the venue is chosen: vendor its style into the paper and add any missing packages
  (docs/typesetting.md, "Known gaps").
