# /// script
# requires-python = "==3.11.*"
# dependencies = ["matplotlib==3.9.2", "numpy==2.1.3"]
# ///
"""Figure 3: what went wrong, by cause. Usage: incidents.py OUT.pdf

Every dated lesson in the eight lead playbooks, hand-coded (evidence/incidents.json), per
cause class: distinct incidents, distinct practices and the user's directives, and copies
of a lesson into another repo (or a second lesson about the same event), counted under the
original's cause. Totals labelled at the bar end. Colours: the first three slots of the
dataviz reference order (validated light, all pairs).
"""

import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

EV = Path(__file__).resolve().parent.parent / "evidence"
COLS = ["#2a78d6", "#eb6834", "#1baf7a"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})

inc = json.loads((EV / "incidents.json").read_text())["lessons"]
by_id = {r["id"]: r for r in inc}
incident, practice, copies = Counter(), Counter(), Counter()
for r in inc:
    if r["same_event_as"]:
        copies[by_id[r["same_event_as"]]["cause_class"]] += 1
    elif r["kind"] == "incident":
        incident[r["cause_class"]] += 1
    else:
        practice[r["cause_class"]] += 1
classes = sorted(set(incident) | set(practice) | set(copies),
                 key=lambda c: (incident[c] + practice[c] + copies[c], incident[c], c))
fig, ax = plt.subplots(figsize=(6.0, 3.0))
left = [0] * len(classes)
for col, (label, cnt) in zip(COLS, [("distinct incident", incident),
                                    ("practice or the user's directive", practice),
                                    ("copied to another repo / same event", copies)]):
    vals = [cnt[c] for c in classes]
    ax.barh(classes, vals, left=left, color=col, label=label, edgecolor=SURFACE,
            linewidth=0.8, height=0.7, zorder=2)
    left = [p + q for p, q in zip(left, vals)]
for y, tot in enumerate(left):
    ax.text(tot + 0.25, y, str(tot), va="center", fontsize=7, color=INK2)
ax.set_xlabel("dated lessons (count)")
ax.set_xlim(0, max(left) + 2)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)
ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=6.8, loc="lower right", labelcolor=INK2)
fig.savefig(sys.argv[1], bbox_inches="tight",
            metadata={"CreationDate": None, "Creator": None, "Producer": None})
