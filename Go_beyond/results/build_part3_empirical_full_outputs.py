from pathlib import Path
import csv
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
DATASETS = ["InVS15", "LH10", "SFHH", "Thiers13"]
DATASET_TITLES = {
    "InVS15": "Workplace (InVS15)",
    "LH10": "Conference (LH10)",
    "SFHH": "Hospital (SFHH)",
    "Thiers13": "High School (Thiers13)",
}
apply_style()
FIGURES_DIR, RESULTS_DIR = ensure_output_dirs()


def load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def save_summary_table(payloads):
    out = RESULTS_DIR / f"part3_empirical_full_sweep_table_{PROFILE}.csv"
    with out.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "dataset",
                "dimension",
                "dataset_path",
                "n_realizations",
                "n_simulations_per_realization",
                "avg_k1",
                "avg_k2",
                "avg_k3",
                "max_rho",
                "first_nonzero_lambda",
            ]
        )
        for dataset in DATASETS:
            for dimension in [2, 3]:
                payload = payloads[(dataset, dimension)]
                summary = payload["summary"]
                avg_rhos = np.array(summary["avg_rhos"], dtype=float)
                nonzero_idx = np.flatnonzero(avg_rhos > 1e-6)
                first_nonzero = float(LAMBDA1S[nonzero_idx[0]]) if len(nonzero_idx) else ""
                writer.writerow(
                    [
                        dataset,
                        dimension,
                        payload["dataset_path"],
                        payload["n_realizations"],
                        payload["n_simulations_per_realization"],
                        summary["avg_k1"],
                        summary["avg_k2"],
                        summary["avg_k3"],
                        float(avg_rhos.max()) if len(avg_rhos) else 0.0,
                        first_nonzero,
                    ]
                )
    return out


def build_figure(payloads):
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.2), sharex=True, sharey=True)
    styles = {
        2: dict(marker="o", color="black", mfc="white", label="Imported D=2"),
        3: dict(marker="s", color="cornflowerblue", mfc="white", label="Imported D=3"),
    }

    for ax, dataset in zip(axes.flat, DATASETS):
        for dimension in [2, 3]:
            payload = payloads[(dataset, dimension)]
            summary = payload["summary"]
            sty = styles[dimension].copy()
            label = sty.pop("label")
            color = sty["color"]
            mfc = sty.pop("mfc")
            ax.plot(LAMBDA1S, summary["avg_rhos"], "-", linewidth=1.2, ms=5.5, mfc=mfc, **sty, label=label)
            ax.errorbar(
                LAMBDA1S,
                summary["avg_rhos"],
                yerr=summary["sem_rhos"],
                fmt="none",
                color=color,
                alpha=0.60,
                capsize=3,
                elinewidth=1.0,
            )
        ax.set_title(DATASET_TITLES[dataset], fontsize=11)
        ax.set_xlim(0.2, 2.2)
        ax.set_ylim(-0.01, 0.9)
        ax.text(
            0.03,
            0.05,
            f"D=3 avg_k3={payloads[(dataset, 3)]['summary']['avg_k3']:.2f}",
            transform=ax.transAxes,
            fontsize=8.5,
        )

    axes[0, 0].set_ylabel("Density of infected nodes, rho*", fontsize=12)
    axes[1, 0].set_ylabel("Density of infected nodes, rho*", fontsize=12)
    axes[1, 0].set_xlabel("Rescaled infectivity, lambda", fontsize=12)
    axes[1, 1].set_xlabel("Rescaled infectivity, lambda", fontsize=12)
    axes[0, 1].legend(fontsize=8.5, loc="upper left", handlelength=1.1, handletextpad=0.4)
    plt.suptitle("Part 3 full empirical sweep across all four datasets", fontsize=13)
    plt.tight_layout()
    fig_path = FIGURES_DIR / f"part3_empirical_full_sweep_{PROFILE}.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return fig_path


def main():
    payloads = {}
    for dataset in DATASETS:
        for dimension in [2, 3]:
            path = RESULTS_DIR / f"part3_{dataset}_D{dimension}_full_sweep_{PROFILE}.pkl"
            payloads[(dataset, dimension)] = load_pickle(path)

    fig_path = build_figure(payloads)
    table_path = save_summary_table(payloads)
    bundle_path = RESULTS_DIR / f"part3_empirical_full_sweep_{PROFILE}.pkl"
    with bundle_path.open("wb") as handle:
        pickle.dump(payloads, handle)
    print(fig_path)
    print(table_path)
    print(bundle_path)


if __name__ == "__main__":
    main()
