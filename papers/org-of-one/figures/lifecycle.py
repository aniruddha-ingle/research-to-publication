# /// script
# requires-python = "==3.11.*"
# dependencies = ["matplotlib==3.9.2", "numpy==2.1.3"]
# ///
"""Figure 2: how long a node took. Usage: lifecycle.py OUT.pdf

Per department, every merged node's lead time in hours (log scale), from the board's git
history (evidence/lifecycle.json): (a) first seen as todo -> first merged; (b) first
claimed/building -> first merged. One dot per node, median as a bar, n on the right.
Departments with no merged node (design-manufacture-interface) and those without a board
(product-in-picture, gateway) are absent. Jitter is deterministic (seed 0).
Times under one minute are drawn at the 1-minute floor (left edge, labelled \u22641 min).
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

EV = Path(__file__).resolve().parent.parent / "evidence"
DOT, INK, INK2, GRID, SURFACE = "#2a78d6", "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
ORDER = ["studio", "mir-triage", "copy-in-product-picture", "product-in-video",
         "research-to-publication"]
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.titlelocation": "left"})

life = json.loads((EV / "lifecycle.json").read_text())["repos"]
rng = np.random.default_rng(0)
fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6), sharey=True, gridspec_kw={"wspace": 0.16})
panels = [("todo_to_merged_h", "(a) todo → merged"),
          ("claimed_to_merged_h", "(b) claimed/building → merged")]
for ax, (key, title) in zip(axes, panels):
    for i, repo in enumerate(ORDER):
        vals = np.array(life[repo]["lead_time_hours_values"].get(key, []))
        y = len(ORDER) - 1 - i
        if len(vals):
            vals = np.maximum(vals, 1 / 60)  # floor at one minute for the log axis
            jit = rng.uniform(-0.22, 0.22, len(vals))
            ax.scatter(vals, y + jit, s=14, color=DOT, edgecolor=SURFACE, linewidth=0.6,
                       alpha=0.85, zorder=3)
            med = float(np.median(vals))
            ax.plot([med, med], [y - 0.34, y + 0.34], color=INK, linewidth=1.6, zorder=4)
        ax.text(0.99, y + 0.3, f"n={len(vals)}", transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=6.5, color=INK2)
    ax.set_xscale("log")
    ax.set_xlim(1 / 60, 100)
    ax.set_xticks([1 / 60, 0.1, 1, 10])
    ax.set_xticklabels(["\u22641 min", "6 min", "1 h", "10 h"])
    ax.set_xlabel("lead time (hours, log scale)")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
axes[0].set_yticks(range(len(ORDER)))
axes[0].set_yticklabels(list(reversed(ORDER)))
axes[0].set_ylim(-0.6, len(ORDER) - 0.4)
fig.savefig(sys.argv[1], bbox_inches="tight",
            metadata={"CreationDate": None, "Creator": None, "Producer": None})
