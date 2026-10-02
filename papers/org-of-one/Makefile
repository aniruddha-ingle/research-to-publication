# Builds this paper from sources: figures from their scripts, then the PDF.
# Pinned toolchain: docs/typesetting.md. Output goes to build/ (gitignored, never committed).
#   make            figures + PDF (build/main.pdf)
#   make figures    regenerate every figure from its script
#   make check      the toolchain is the pinned one
#   make clean      remove build/

TEX_PIN   := TeX Live 2022
PY_PIN    := 3.11
BUILD     := build
FIG_SRC   := $(wildcard figures/*.py)
FIG_PDF   := $(patsubst figures/%.py,$(BUILD)/figures/%.pdf,$(FIG_SRC))
TAB_SRC   := $(wildcard tables/*.py)
TAB_TEX   := $(patsubst tables/%.py,$(BUILD)/tables/%.tex,$(TAB_SRC))
EVIDENCE  := $(wildcard evidence/*.json)

.PHONY: all figures tables check clean
all: $(BUILD)/main.pdf

check:
	@pdflatex --version | head -1 | grep -q "$(TEX_PIN)" || { echo "pdflatex is not $(TEX_PIN): see docs/typesetting.md"; exit 1; }
	@command -v latexmk >/dev/null && command -v bibtex >/dev/null && command -v uv >/dev/null || { echo "need latexmk, bibtex, uv"; exit 1; }

figures: $(FIG_PDF)

# Each figure script is a uv script (PEP 723 deps, wheels only) that writes the path it is given.
$(BUILD)/figures/%.pdf: figures/%.py $(EVIDENCE) | check
	@mkdir -p $(dir $@)
	UV_NO_BUILD=1 uv run --quiet --python $(PY_PIN) --script $< $@

# Tables generated from evidence (stdlib-only uv scripts), \input by main.tex.
tables: $(TAB_TEX)
$(BUILD)/tables/%.tex: tables/%.py $(EVIDENCE) | check
	@mkdir -p $(dir $@)
	UV_NO_BUILD=1 uv run --quiet --python $(PY_PIN) --script $< $@

$(BUILD)/main.pdf: main.tex refs.bib $(FIG_PDF) $(TAB_TEX) | check
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=$(BUILD) main.tex

clean:
	rm -rf $(BUILD)
