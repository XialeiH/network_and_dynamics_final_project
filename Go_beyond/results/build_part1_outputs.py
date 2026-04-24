from pathlib import Path
import csv
import json
import pickle
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_plotstyle import apply_style, ensure_output_dirs


PROFILE = "production"
LAMBDA1S = np.linspace(0.2, 2.2, 30)
apply_style()
FIGURES_DIR, RESULTS_DIR = ensure_output_dirs()

STYLES = {
    "er": dict(marker="o", color="black", mfc="white", label="ER / RSC"),
    "scale_free": dict(marker="s", color="darkorange", mfc="white", label="Scale-free"),
    "small_world": dict(marker="^", color="cornflowerblue", mfc="white", label="Small-world"),
}


def load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def save_calibration_table(calibration):
    out = RESULTS_DIR / f"part1_calibration_table_{PROFILE}.csv"
    with out.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["family", "generator_mode", "params", "mean_k1", "mean_k2", "score"])
        for family, payload in calibration["families"].items():
            chosen = payload["chosen"]
            writer.writerow([family, chosen["generator_mode"], json.dumps(chosen["params"]), chosen["mean_k1"], chosen["mean_k2"], chosen["score"]])
    return out


def build_main_figure():
    fig = plt.figure(figsize=(4.8, 3.4))
    ax = plt.subplot(111)
    payload = {}
    for family in ["er", "scale_free", "small_world"]:
        path = RESULTS_DIR / f"part1_{family}_lambda2_0p8_seed_5_{PROFILE}_checkpoint.pkl"
        current = load_pickle(path)
        payload[family] = current
        summary = current["summary"]
        sty = STYLES[family].copy()
        label = sty.pop("label")
        color = sty["color"]
        mfc = sty.pop("mfc")
        ax.plot(LAMBDA1S, summary["avg_rhos"], "-", linewidth=1.2, ms=6, mfc=mfc, **sty, label=label)
        ax.errorbar(LAMBDA1S, summary["avg_rhos"], yerr=summary["sem_rhos"], fmt="none", color=color, alpha=0.45, capsize=2, elinewidth=0.8)
    ax.set_xlabel("Rescaled infectivity, lambda", size=12)
    ax.set_ylabel("Density of infected nodes, rho*", size=12)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(-0.01, 0.85)
    ax.legend(fontsize=9, handlelength=1.1, handletextpad=0.4, borderaxespad=0.2, loc="upper left")
    ax.set_title("Calibrated controlled comparison (production)", fontsize=11)
    plt.tight_layout()
    fig_path = FIGURES_DIR / f"network_structures_controlled_calibrated_{PROFILE}.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    with (RESULTS_DIR / f"network_structures_controlled_calibrated_{PROFILE}.pkl").open("wb") as handle:
        pickle.dump(payload, handle)
    return fig_path


def build_high_lambda2_figure():
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6), sharey=True)
    payload = {}
    for ax, seed_pct, title in [
        (axes[0], 1, "Low initial density"),
        (axes[1], 40, "High initial density"),
    ]:
        for family in ["er", "scale_free", "small_world"]:
            path = RESULTS_DIR / f"part1_{family}_lambda2_2p5_seed_{seed_pct}_{PROFILE}_checkpoint.pkl"
            current = load_pickle(path)
            payload[(family, seed_pct)] = current
            summary = current["summary"]
            sty = STYLES[family].copy()
            label = sty.pop("label")
            color = sty["color"]
            mfc = sty.pop("mfc")
            ax.plot(LAMBDA1S, summary["avg_rhos"], "-", linewidth=1.2, ms=5.5, mfc=mfc, **sty, label=label)
            ax.errorbar(LAMBDA1S, summary["avg_rhos"], yerr=summary["sem_rhos"], fmt="none", color=color, alpha=0.40, capsize=2, elinewidth=0.8)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Rescaled infectivity, lambda", fontsize=12)
        ax.set_xlim(0.2, 2.2)
        ax.set_ylim(-0.01, 0.95)
    axes[0].set_ylabel("Density of infected nodes, rho*", fontsize=12)
    axes[1].legend(fontsize=8.5, handlelength=1.1, handletextpad=0.4, loc="upper left")
    plt.suptitle("Calibrated controlled comparison at lambda_delta = 2.5", fontsize=12)
    plt.tight_layout()
    fig_path = FIGURES_DIR / f"network_structures_calibrated_lambda2_2p5_{PROFILE}.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    with (RESULTS_DIR / f"network_structures_calibrated_lambda2_2p5_{PROFILE}.pkl").open("wb") as handle:
        pickle.dump(payload, handle)
    return fig_path


def main():
    calibration_path = RESULTS_DIR / f"part1_calibration_{PROFILE}.json"
    calibration = json.loads(calibration_path.read_text())
    print(save_calibration_table(calibration))
    print(build_main_figure())
    print(build_high_lambda2_figure())


if __name__ == "__main__":
    main()
