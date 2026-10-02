# /// script
# requires-python = "==3.11.*"
# dependencies = ["matplotlib==3.9.2", "numpy==2.1.3"]
# ///
"""Template figure: a synthetic curve. Usage: hello.py OUT.pdf

Real figures read an evidence file (JSON, committed or reproduced into build/) and say so here.
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

out = sys.argv[1]
x = np.linspace(0, 2 * np.pi, 200)
fig, ax = plt.subplots(figsize=(4, 2.5))
ax.plot(x, np.sin(x), color="#2a6f97")
ax.set_xlabel("x")
ax.set_ylabel("sin x")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
# Fixed metadata so the PDF is byte-stable across builds.
fig.savefig(out, metadata={"CreationDate": None, "Creator": None, "Producer": None})
