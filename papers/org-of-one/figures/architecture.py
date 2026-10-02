# /// script
# requires-python = "==3.11.*"
# dependencies = ["matplotlib==3.9.2", "numpy==2.1.3"]
# ///
"""Figure: the system's design (a diagram; reads no data). Usage: architecture.py OUT.pdf

Drawn with matplotlib because the pinned TinyTeX 2022 has no TikZ (docs/typesetting.md).
What it shows comes from studio plan 06 and ADR 0024 at the pinned SHA, the gateway's
CLAUDE.md, and the org's shared rules (see the paper, Section 3). One department is drawn in
full; the others run the same kit.
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
BLUE, ORANGE, GREEN, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"

plt.rcParams.update({"font.size": 7.2, "text.color": INK})
fig, ax = plt.subplots(figsize=(6.8, 4.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 64.5)
ax.axis("off")


def box(x, y, w, h, title, body="", edge=INK2, fill=SURFACE, dashed=False, tsize=7.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8",
                                linewidth=1.0, edgecolor=edge, facecolor=fill,
                                linestyle=(0, (3, 2)) if dashed else "solid", zorder=2))
    ax.text(x + w / 2, y + h - 1.4, title, ha="center", va="top", fontsize=tsize,
            fontweight="bold", zorder=3)
    if body:
        ax.text(x + w / 2, y + h - 4.2, body, ha="center", va="top", fontsize=6.3,
                color=INK2, linespacing=1.25, zorder=3)


def arrow(x1, y1, x2, y2, label="", color=INK2, dashed=False, lx=0, ly=0, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=8,
                                 linewidth=0.9, color=color, zorder=1,
                                 connectionstyle=f"arc3,rad={rad}",
                                 linestyle=(0, (3, 2)) if dashed else "solid"))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, ha="center", va="center",
                fontsize=6.0, color=color, zorder=4,
                bbox=dict(boxstyle="square,pad=0.15", fc=SURFACE, ec="none"))


# The human and the gateway.
box(2, 52, 22, 11, "The user", "steers from a phone;\ntaste calls; approvals\n(spend, deletes, people)",
    edge=ORANGE)
box(36, 52, 22, 11, "Gateway session", "relays direction word for\nword; builds nothing;\nnever relays approval",
    edge=ORANGE)
arrow(24, 57.5, 36, 57.5, "direction", ly=1.6)
arrow(13, 52, 13, 39.4, "approval only in\nthe lead's own\nsession", color=ORANGE, lx=-6.2, ly=1.5)
arrow(47, 52, 47, 39.4, "direction", lx=4.6, ly=1.5)

# One department (studio drawn; others run the same kit).
ax.add_patch(FancyBboxPatch((0.5, 0.5), 99, 43, boxstyle="round,pad=0.3,rounding_size=1.0",
                            linewidth=0.8, edgecolor=GRID, facecolor="#fafaf8", zorder=0))
ax.text(98.5, 43.2, "one department = one git repository (the kit is copied into 6 repos)",
        ha="right", va="top", fontsize=6.3, color=INK2, style="italic")

box(2, 28.5, 26, 11, "Lead sessions (N)", "lead-1 ... lead-13;\nplan first; claim, then\ndispatch agents", edge=BLUE)
box(36, 28.5, 22, 11, "Board in git", "graph.yaml: nodes,\ndepends_on, touches\nglobs, state", edge=BLUE)
box(66, 28.5, 32, 11, "Claims and locks (Mac only)", "atomic mkdir claims per node\nand number; mutexes: integrate,\ndeploy, heavy-test",
    edge=BLUE)
arrow(28, 34, 36, 34, "ready?", ly=1.6)
arrow(58, 34, 66, 34, "claim", ly=1.6)

box(2, 14, 26, 11, "Builder agents", "one git worktree\nper node", edge=GREEN)
box(36, 14, 22, 11, "Reviewer agent", "never edits; writes\na PASS marker", edge=GREEN)
box(66, 14, 32, 11, "integrate.sh (under lock)", "merge trunk into branch; tests;\nPASS required; stops on conflict;\nmerge --no-ff; board: merged",
    edge=YELLOW)
arrow(15, 28.5, 15, 25, "dispatch", lx=5.2)
arrow(28, 19.5, 36, 19.5, "review", ly=1.6)
arrow(58, 19.5, 66, 19.5, "PASS", ly=1.6)

box(2, 1.5, 34, 9.5, "Lead playbook (in git)", "dated Lessons: each incident's\nfix written back as a rule",
    edge=INK2, dashed=True)
box(42, 1.5, 18, 9.5, "Live app", "main + every\nbuilt node", edge=ORANGE)
box(66, 1.5, 32, 9.5, "Trunk (main)", "pre-push hook refuses media,\ndata, big files, secrets", edge=INK2)
arrow(82, 14, 82, 11.0, "")
arrow(66, 6.0, 60, 6.0, "main", ly=1.5)
arrow(24, 14, 46, 11.0, "deploy at built", dashed=True, lx=5.5, ly=1.0)

fig.savefig(sys.argv[1], bbox_inches="tight",
            metadata={"CreationDate": None, "Creator": None, "Producer": None})
