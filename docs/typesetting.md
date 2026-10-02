# Typesetting (pinned 2026-10-02, plan 01, research-lead-1)

**Pinned:** TeX Live 2022 via TinyTeX (`~/Library/TinyTeX`, already on this Mac since 2022:
prebuilt `universal-darwin` binaries, no source build, no new install): `pdflatex` (pdfTeX
1.40.24), `bibtex` 0.99d, `latexmk` 4.77. Figures: Python 3.11 under `uv` with PEP 723
inline, version-pinned dependencies, built with `UV_NO_BUILD=1` (wheels only).
All open source (LPPL/GPL, matplotlib PSF-style, numpy BSD). No cost.

`make check` in a paper refuses any other TeX version.

## A paper's build
```
papers/<slug>/
  main.tex  refs.bib  Makefile      (copy from papers/_template)
  figures/<name>.py                 one script per figure: reads evidence, writes build/figures/<name>.pdf
  build/                            gitignored: figures and main.pdf, never committed
```
`make` regenerates every figure from its script, then the PDF. `make clean && make` must work
from a fresh checkout; that is the full gate's "builds from sources" check.

Evidence a figure reads: JSON (or another text format) committed next to the paper when it
is ours and public-safe, or written into `build/` by the reproducer's script. `*.csv` and
`data/` are gitignored and refused by the pre-push hook on purpose.

Figure PDFs are saved with fixed metadata so a rebuild is byte-identical (checked on the
template: same md5 twice).

## Why this and not the alternatives
- **TinyTeX 2022 (chosen):** already installed, prebuilt, nothing to download for the
  template. Proven: the template builds in ~3 s with zero warnings.
- **Tectonic:** a single self-contained engine with an Intel Mac binary; fetches a pinned
  bundle from the network on first use. The fallback if a venue class needs packages TinyTeX
  2022 can't get.
- **pandoc → LaTeX:** convenient for drafts, but venue templates are LaTeX; one less layer.
- **Typst:** fast and open source, but venues (ISMIR, ACM, IEEE, arXiv) want LaTeX sources.

## Known gaps in this TinyTeX (as of the pin)
Missing: `microtype`, `newtx`, `siunitx`, `caption`/`subcaption`, `cleveref`, `lm`, and the
Courier metrics (so `times`/`mathptmx` with T1 fail). Venue classes (`acmart`, `IEEEtran`,
the ISMIR style) are not installed.

Adding one, in order of preference:
1. **Vendor the venue's class/style file into the paper directory** (they are LPPL source
   files that venues distribute for exactly this). No install.
2. `tlmgr install <pkg>` against the frozen 2022 repository (TeX Live 2022's tlmgr can't
   use the current one):
   `tlmgr option repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2022/tlnet-final`
   then `tlmgr install <pkg>`. Free, prebuilt, user-local. Record each one here.
3. Tectonic, if 1–2 fail. Record the switch here and in the plan.

## Not available here
No PDF rasteriser (poppler) on the Mac, so Claude can't look at a rendered page; checks are
the build log (warnings, undefined refs/citations) and the `.bbl`.
