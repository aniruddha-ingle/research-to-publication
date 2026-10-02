# /// script
# requires-python = "==3.11.*"
# dependencies = ["matplotlib==3.9.2", "numpy==2.1.3"]
# ///
"""Figure 1: the week. Usage: timeline.py OUT.pdf

(a) Commits per day per repository (committed history: evidence/scale.json).
(b) Concurrent studio lead sessions per hour: committed history (a lead's first to last
    commit that names it in the subject, evidence/leads.json) and, dashed, the observational
    variant that starts each session when its lead number was reserved
    (evidence/studio_state.json, studio's uncommitted state; drawn only if present).
Colours: the dataviz reference categorical order (validated light, adjacent pairs).
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

EV = Path(__file__).resolve().parent.parent / "evidence"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7",
          "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
REPOS = [("studio", "studio"), ("mir-triage", "mir-triage"),
         ("copy-in-product-picture", "copy-in-product-picture"),
         ("product-in-picture", "product-in-picture"), ("product-in-video", "product-in-video"),
         ("design-manufacture-interface", "design-manufacture-interface"),
         ("gateway", "gateway"), ("research-to-publication", "research-to-publication")]

plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.titlelocation": "left"})

scale = json.loads((EV / "scale.json").read_text())["repos"]
leads = json.loads((EV / "leads.json").read_text())["repos"]["studio"]
state_file = EV / "studio_state.json"
state = json.loads(state_file.read_text()) if state_file.exists() else None

days = sorted({d for r, _ in REPOS for d in scale[r]["commits_per_day"]})
x_days = [datetime.fromisoformat(d) + timedelta(hours=12) for d in days]

fig, (a, b) = plt.subplots(2, 1, figsize=(6.6, 4.6), sharex=True,
                           gridspec_kw={"height_ratios": [3, 2], "hspace": 0.32})
bottom = [0] * len(days)
for i, (repo, label) in enumerate(REPOS):
    ys = [scale[repo]["commits_per_day"].get(d, 0) for d in days]
    a.bar(x_days, ys, width=0.78, bottom=bottom, color=SERIES[i], label=label,
          edgecolor=SURFACE, linewidth=0.8, zorder=2)
    bottom = [p + q for p, q in zip(bottom, ys)]
for xd, tot in zip(x_days, bottom):
    a.text(xd, tot + 8, f"{tot}", ha="center", va="bottom", fontsize=7, color=INK2)
a.set_ylabel("commits per day")
a.set_ylim(0, max(bottom) * 1.15)
a.set_title("(a) Commits per day, all eight repositories (committed history)")
a.legend(ncols=1, fontsize=6.5, frameon=False, loc="upper left", handlelength=1.0,
         labelcolor=INK2)


def hourly(per_hour):
    xs = [datetime.strptime(h, "%Y-%m-%dT%H") for h in per_hour]
    return xs, list(per_hour.values())


xs, ys = hourly(leads["concurrency_from_spans"]["per_hour"])
b.step(xs, ys, where="post", color=SERIES[0], linewidth=1.6,
       label="first to last attributed commit (committed history)", zorder=3)
if state:
    xs2, ys2 = hourly(state["concurrency_reserved_to_last_commit"]["per_hour"])
    b.step(xs2, ys2, where="post", color=SERIES[1], linewidth=1.2, linestyle=(0, (3, 2)),
           label="from number reserved (studio state, observational)", zorder=2)
b.set_ylabel("studio leads\nat once")
b.set_yticks(range(0, 6))
b.set_ylim(0, 5.6)
b.set_title("(b) Concurrent studio lead sessions per hour")
b.legend(fontsize=6.5, frameon=False, loc="upper left", labelcolor=INK2)

for ax in (a, b):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
b.xaxis.set_major_locator(mdates.DayLocator())
b.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
b.set_xlim(datetime.fromisoformat(days[0]) - timedelta(hours=2),
           datetime.fromisoformat(days[-1]) + timedelta(hours=26))
b.set_xlabel("date (America/New_York, 2026)")
fig.savefig(sys.argv[1], bbox_inches="tight",
            metadata={"CreationDate": None, "Creator": None, "Producer": None})
