from pathlib import Path
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
FIGURES_DIR, RESULTS_DIR = ensure_output_dirs()
apply_style()


def load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def build_synthetic_figure():
    payload_low = load_pickle(RESULTS_DIR / f"d3_synthetic_bistability_lambda2_1p2_lambda3_1p2_seed_1_{PROFILE}.pkl")
    payload_high = load_pickle(RESULTS_DIR / f"d3_synthetic_bistability_lambda2_1p2_lambda3_1p2_seed_40_{PROFILE}.pkl")

    fig = plt.figure(figsize=(4.8, 3.4))
    ax = plt.subplot(111)
    styles = {
        "low": dict(color="black", marker="o", mfc="white", label="Low seed (rho0=0.01)"),
        "high": dict(color="darkorange", marker="s", mfc="white", label="High seed (rho0=0.40)"),
    }
    for label, payload in [("low", payload_low), ("high", payload_high)]:
        summary = payload["summary"]
        sty = styles[label]
        ax.plot(
            LAMBDA1S,
            summary["avg_rhos"],
            "-",
            color=sty["color"],
            marker=sty["marker"],
            mfc=sty["mfc"],
            ms=6,
            linewidth=1.2,
            label=sty["label"],
        )
        ax.errorbar(
            LAMBDA1S,
            summary["avg_rhos"],
            yerr=summary["sem_rhos"],
            fmt="none",
            color=sty["color"],
            alpha=0.60,
            capsize=3,
            elinewidth=1.0,
        )
    ax.set_xlabel("Rescaled infectivity, lambda", fontsize=12)
    ax.set_ylabel("Density of infected nodes, rho*", fontsize=12)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(-0.01, 0.9)
    ax.legend(fontsize=8.5, loc="upper left", handlelength=1.1, handletextpad=0.4)
    ax.set_title("Synthetic D=3 bistability scan", fontsize=11)
    plt.tight_layout()
    out = FIGURES_DIR / f"d3_synthetic_bistability_lambda2_1p2_lambda3_1p2_{PROFILE}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def build_time_figure():
    payload = load_pickle(RESULTS_DIR / f"d3_time_evolution_bistable_lambda2_1p2_lambda3_1p2_{PROFILE}.pkl")
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(payload["histories"])))
    for color, record in zip(colors, payload["histories"]):
        ax.plot(range(len(record["history"])), record["history"], "-", color=color, lw=1.2, label=f"rho0={record['rho0']:.2f}")
    if payload["unstable_root"] is not None:
        ax.axhline(payload["unstable_root"], color="crimson", linestyle="--", linewidth=1.1, label="Unstable mean-field root")
    ax.set_xlabel("Time steps", fontsize=12)
    ax.set_ylabel("Density of infected nodes rho(t)", fontsize=12)
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(f"Synthetic D=3 bistable time evolution (lambda={payload['lambda1']:.3f})", fontsize=11)
    ax.legend(fontsize=8, loc="upper right", handlelength=1.2, labelspacing=0.2)
    plt.tight_layout()
    out = FIGURES_DIR / f"d3_time_evolution_bistable_lambda2_1p2_lambda3_1p2_{PROFILE}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def build_empirical_figure_if_available():
    best_path = RESULTS_DIR / f"part3_empirical_best_d3_comparison_{PROFILE}.pkl"
    if not best_path.exists():
        return None
    payload = load_pickle(best_path)
    fig = plt.figure(figsize=(4.8, 3.4))
    ax = plt.subplot(111)
    styles = {
        "Imported D=2": dict(color="black", marker="o", mfc="white"),
        "Imported D=3": dict(color="cornflowerblue", marker="s", mfc="white"),
    }
    for label, run_payload in payload["runs"].items():
        summary = run_payload["summary"]
        sty = styles[label]
        ax.plot(LAMBDA1S, summary["avg_rhos"], "-", linewidth=1.2, ms=6, **sty, label=label)
        ax.errorbar(
            LAMBDA1S,
            summary["avg_rhos"],
            yerr=summary["sem_rhos"],
            fmt="none",
            color=sty["color"],
            alpha=0.60,
            capsize=3,
            elinewidth=1.0,
        )
    best = payload["best_positive"]
    ax.set_xlabel("Rescaled infectivity, lambda", fontsize=12)
    ax.set_ylabel("Density of infected nodes, rho*", fontsize=12)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(-0.01, 0.9)
    ax.legend(fontsize=8.5, loc="upper left", handlelength=1.1, handletextpad=0.4)
    ax.set_title(f"Empirical best D=3 file: {best['dataset_name']} r={best['realization_index']}", fontsize=11)
    plt.tight_layout()
    out = FIGURES_DIR / f"part3_empirical_best_d3_comparison_{PROFILE}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    empirical_figure = build_empirical_figure_if_available()
    outputs = {
        "synthetic_figure": str(build_synthetic_figure()),
        "time_figure": str(build_time_figure()),
        "empirical_figure": str(empirical_figure) if empirical_figure else None,
        "empirical_search_csv": str(RESULTS_DIR / f"part3_empirical_tetrahedron_search_{PROFILE}.csv"),
        "empirical_search_json": str(RESULTS_DIR / f"part3_empirical_tetrahedron_search_{PROFILE}.json"),
        "empirical_diagnostic_json": str(RESULTS_DIR / f"part3_empirical_diagnostic_{PROFILE}.json"),
        "synthetic_calibration_json": str(RESULTS_DIR / f"part3_synthetic_calibration_{PROFILE}.json"),
        "synthetic_calibration_csv": str(RESULTS_DIR / f"part3_synthetic_calibration_table_{PROFILE}.csv"),
    }
    summary_path = RESULTS_DIR / f"part3_gpu_improved_outputs_{PROFILE}.json"
    summary_path.write_text(json.dumps(outputs, indent=2))
    print(summary_path)


if __name__ == "__main__":
    main()
