from argparse import ArgumentParser
from pathlib import Path
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_experiments import run_prevalence_scan, run_time_evolution_scan, save_pickle
from core.go_beyond_generators import generate_family_complex
from core.go_beyond_import import import_sociopatterns_complex
from core.go_beyond_plotstyle import apply_style, ensure_output_dirs
from core.go_beyond_results import parse_results


apply_style()
FIGURES_DIR, RESULTS_DIR = ensure_output_dirs()
DATASET_PATH = ROOT.parent / "Data" / "Sociopatterns" / "thr_data_random" / "random_5_0.8min_cliques_Thiers13.json"

N = 2000
MU = 0.05
T_MAX = 4000
N_SIMS = 80
N_WORKERS = 16
LAMBDA1S = np.linspace(0.2, 2.2, 30)
LAMBDA2_TARGET = 0.8
LAMBDA3_LIST = [0.0, 0.6, 1.2]
SEED_PCT = 5
EMPIRICAL_T_MAX = 4000
EMPIRICAL_N_SIMS = 80
TIME_T_MAX = 4000
PROFILE = "production"


def synthetic_complex():
    return generate_family_complex(
        family="er",
        mode="controlled",
        n_nodes=N,
        max_dimension=3,
        seed=31,
        k1=16,
        k2=4,
        k3=1.5,
    )


def run_synthetic():
    out = RESULTS_DIR / f"d3_synthetic_{PROFILE}.pkl"
    if out.exists():
        print(f"skip existing {out.name}")
        return
    complex_data = synthetic_complex()
    synthetic_runs = {}
    for idx, lambda3_target in enumerate(LAMBDA3_LIST):
        print(f"synthetic lambda3={lambda3_target}")
        results = run_prevalence_scan(
            complex_data,
            lambda1s=LAMBDA1S,
            lambda2_target=LAMBDA2_TARGET,
            lambda3_target=lambda3_target,
            seed_pct=SEED_PCT,
            t_max=T_MAX,
            mu=MU,
            n_sims=N_SIMS,
            n_workers=N_WORKERS,
            base_seed=3100 + idx * 100,
        )
        synthetic_runs[lambda3_target] = {
            "results": results,
            "summary": parse_results(results, cut=False),
        }
    save_pickle(out, {"complex": complex_data, "runs": synthetic_runs})

    fig = plt.figure(figsize=(4.8, 3.4))
    ax = plt.subplot(111)
    colors = {0.0: "black", 0.6: "gray", 1.2: "darkorange"}
    markers = {0.0: "o", 0.6: "^", 1.2: "s"}
    for lambda3_target, payload in synthetic_runs.items():
        summary = payload["summary"]
        ax.plot(
            LAMBDA1S,
            summary["avg_rhos"],
            "-",
            marker=markers[lambda3_target],
            color=colors[lambda3_target],
            mfc="white",
            ms=6,
            linewidth=1.2,
            label=f"lambda3={lambda3_target}",
        )
        ax.errorbar(
            LAMBDA1S,
            summary["avg_rhos"],
            yerr=summary["sem_rhos"],
            fmt="none",
            color=colors[lambda3_target],
            alpha=0.45,
            capsize=2,
            elinewidth=0.8,
        )
    ax.set_xlabel("Rescaled infectivity, lambda", size=12)
    ax.set_ylabel("Density of infected nodes, rho*", size=12)
    ax.set_xlim(float(LAMBDA1S.min()), float(LAMBDA1S.max()))
    ax.set_ylim(-0.01, 0.9)
    ax.legend(fontsize=9, loc="upper left", handlelength=1.1, handletextpad=0.4)
    ax.set_title("Synthetic D=3 tetrahedron study (production)", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"d3_synthetic_prevalence_{PROFILE}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_empirical():
    out = RESULTS_DIR / f"d3_empirical_example_{PROFILE}.pkl"
    if out.exists():
        print(f"skip existing {out.name}")
        return
    if not DATASET_PATH.exists():
        raise FileNotFoundError(DATASET_PATH)
    empirical_d2 = import_sociopatterns_complex(DATASET_PATH, max_dimension=2, seed=5)
    empirical_d3 = import_sociopatterns_complex(DATASET_PATH, max_dimension=3, seed=5)
    empirical_runs = {}
    for idx, (label, complex_data, lambda3_target) in enumerate(
        [("Imported D=2", empirical_d2, 0.0), ("Imported D=3", empirical_d3, 0.8)]
    ):
        print(f"empirical {label}")
        results = run_prevalence_scan(
            complex_data,
            lambda1s=LAMBDA1S,
            lambda2_target=LAMBDA2_TARGET,
            lambda3_target=lambda3_target,
            seed_pct=SEED_PCT,
            t_max=EMPIRICAL_T_MAX,
            mu=MU,
            n_sims=EMPIRICAL_N_SIMS,
            n_workers=N_WORKERS,
            base_seed=4100 + idx * 100,
        )
        empirical_runs[label] = {
            "complex_data": complex_data,
            "summary": parse_results(results, cut=False),
            "results": results,
        }
    save_pickle(out, empirical_runs)

    fig = plt.figure(figsize=(4.8, 3.4))
    ax = plt.subplot(111)
    emp_styles = {
        "Imported D=2": dict(marker="o", color="black", mfc="white"),
        "Imported D=3": dict(marker="s", color="cornflowerblue", mfc="white"),
    }
    for label, payload in empirical_runs.items():
        summary = payload["summary"]
        sty = emp_styles[label]
        ax.plot(LAMBDA1S, summary["avg_rhos"], "-", linewidth=1.2, ms=6, **sty, label=label)
        ax.errorbar(
            LAMBDA1S,
            summary["avg_rhos"],
            yerr=summary["sem_rhos"],
            fmt="none",
            color=sty["color"],
            alpha=0.45,
            capsize=2,
            elinewidth=0.8,
        )
    ax.set_xlabel("Rescaled infectivity, lambda", size=12)
    ax.set_ylabel("Density of infected nodes, rho*", size=12)
    ax.set_xlim(float(LAMBDA1S.min()), float(LAMBDA1S.max()))
    ax.set_ylim(-0.01, 0.9)
    ax.legend(fontsize=9, loc="upper left", handlelength=1.1, handletextpad=0.4)
    ax.set_title("Imported simplices: D=2 vs D=3 (production)", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"d3_imported_comparison_{PROFILE}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_time_evolution():
    out = RESULTS_DIR / f"d3_time_evolution_{PROFILE}.pkl"
    if out.exists():
        print(f"skip existing {out.name}")
        return
    time_histories = run_time_evolution_scan(
        synthetic_complex(),
        lambda_target=0.85,
        lambda2_target=LAMBDA2_TARGET,
        lambda3_target=1.2,
        rho0_list=np.linspace(0.0, 1.0, 7),
        t_max=TIME_T_MAX,
        mu=MU,
        n_workers=min(N_WORKERS, 7),
        base_seed=5100,
    )
    save_pickle(out, time_histories)

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(time_histories)))
    for color, payload in zip(colors, time_histories):
        ax.plot(
            range(len(payload["history"])),
            payload["history"],
            "-",
            color=color,
            lw=1.2,
            label=f"rho0={payload['rho0']:.2f}",
        )
    ax.set_xlabel("Time steps", fontsize=12)
    ax.set_ylabel("Density of infected nodes rho(t)", fontsize=12)
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("Synthetic D=3 time evolution (production)", fontsize=11)
    ax.legend(fontsize=8, loc="upper right", handlelength=1.2, labelspacing=0.2)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"d3_time_evolution_{PROFILE}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--component", choices=["synthetic", "empirical", "time_evolution"], required=True)
    args = parser.parse_args()
    if args.component == "synthetic":
        run_synthetic()
    elif args.component == "empirical":
        run_empirical()
    else:
        run_time_evolution()
