from pathlib import Path
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_analytic import classify_fixed_points, fold_surface_from_rho_lambda3
from core.go_beyond_plotstyle import apply_style, ensure_output_dirs


apply_style()
FIGURES_DIR, RESULTS_DIR = ensure_output_dirs()

LAMBDA3 = 1.2
LAMBDA1S = np.linspace(0.0, 2.2, 320)
LAMBDA2S = np.linspace(0.0, 2.2, 320)
PRODUCTION_LAMBDA2 = 0.8


def stable_endemic_density(lambda1, lambda2, lambda3):
    fixed_points = classify_fixed_points(float(lambda1), float(lambda2), float(lambda3))
    positive_stable = [fp.rho for fp in fixed_points[1:] if fp.stable]
    if not positive_stable:
        return 0.0
    return max(positive_stable)


heatmap = np.zeros((len(LAMBDA2S), len(LAMBDA1S)))
for row, lambda2 in enumerate(LAMBDA2S):
    for col, lambda1 in enumerate(LAMBDA1S):
        heatmap[row, col] = stable_endemic_density(lambda1, lambda2, LAMBDA3)

rho_curve = np.linspace(1e-3, 0.999, 4000)
fold_lambda1, fold_lambda2 = fold_surface_from_rho_lambda3(rho_curve, LAMBDA3)
mask = (
    np.isfinite(fold_lambda1)
    & np.isfinite(fold_lambda2)
    & (fold_lambda1 >= LAMBDA1S.min())
    & (fold_lambda1 <= LAMBDA1S.max())
    & (fold_lambda2 >= LAMBDA2S.min())
    & (fold_lambda2 <= LAMBDA2S.max())
)
fold_lambda1 = fold_lambda1[mask]
fold_lambda2 = fold_lambda2[mask]

fig, ax = plt.subplots(figsize=(5.3, 4.1))
im = ax.imshow(
    heatmap,
    origin="lower",
    extent=[LAMBDA1S.min(), LAMBDA1S.max(), LAMBDA2S.min(), LAMBDA2S.max()],
    aspect="auto",
    cmap="viridis",
    vmin=0.0,
    vmax=max(0.8, float(heatmap.max())),
)

if len(fold_lambda1) > 0:
    order = np.argsort(fold_lambda1)
    ax.plot(
        fold_lambda1[order],
        fold_lambda2[order],
        color="white",
        linewidth=2.0,
        linestyle="--",
        label=r"Fold boundary",
    )

ax.axvline(1.0, color="white", linestyle=":", linewidth=1.2, alpha=0.9)
ax.axhline(PRODUCTION_LAMBDA2, color="white", linestyle=":", linewidth=1.2, alpha=0.9)
ax.text(1.03, 0.08, r"$\lambda=1$", color="white", fontsize=10)
ax.text(0.08, PRODUCTION_LAMBDA2 + 0.05, r"$\lambda_\Delta=0.8$", color="white", fontsize=10)

ax.set_title(rf"D=3 phase diagram at fixed $\lambda_3={LAMBDA3}$", fontsize=12)
ax.set_xlabel(r"Rescaled infectivity $\lambda$", fontsize=12)
ax.set_ylabel(r"Triangle infectivity $\lambda_\Delta$", fontsize=12)
ax.set_xlim(LAMBDA1S.min(), LAMBDA1S.max())
ax.set_ylim(LAMBDA2S.min(), LAMBDA2S.max())
ax.legend(loc="upper left", fontsize=9, frameon=True)

cbar = plt.colorbar(im, ax=ax)
cbar.set_label(r"Stable endemic density $\rho^*$", fontsize=11)

plt.tight_layout()
out = FIGURES_DIR / "d3_phase_diagram_lambda3_1p2.png"
plt.savefig(out, dpi=160, bbox_inches="tight")
print(out)
