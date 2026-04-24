from argparse import ArgumentParser
from pathlib import Path
import json
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_import import import_sociopatterns_complex, load_sociopatterns_realizations
from core.go_beyond_results import parse_results
from core.go_beyond_experiments import save_pickle
from core.go_beyond_torch_higher_order import run_prevalence_scan_torch_higher_order


parser = ArgumentParser()
parser.add_argument("--dataset", required=True, choices=["InVS15", "LH10", "SFHH", "Thiers13"])
parser.add_argument("--max-dimension", type=int, required=True, choices=[2, 3])
parser.add_argument("--device", default="cuda")
args = parser.parse_args()

PROFILE = "production"
MU = 0.05
T_MAX = 4000
N_SIMS = 80
LAMBDA1S = np.linspace(0.2, 2.2, 30)
LAMBDA2_TARGET = 0.8
LAMBDA3_TARGET = 0.8
SEED_PCT = 5
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = ROOT.parent / "Data" / "Sociopatterns" / "thr_data_random"

DATASET_FILES = {
    "InVS15": "random_5_0.8min_cliques_InVS15.json",
    "LH10": "random_5_0.8min_cliques_LH10.json",
    "Thiers13": "random_5_0.8min_cliques_Thiers13.json",
    "SFHH": "random_15_0.85min_cliques_SFHH.json",
}

DATASET_NOTES = {
    "InVS15": "Workplace dataset using the 5-minute, threshold 0.8 clique file.",
    "LH10": "Conference dataset using the 5-minute, threshold 0.8 clique file.",
    "Thiers13": "High-school dataset using the 5-minute, threshold 0.8 clique file.",
    "SFHH": "Hospital dataset using the nearest available file, 15-minute threshold 0.85, because no 5-minute threshold 0.8 file exists.",
}

BASE_SEEDS = {
    ("InVS15", 2): 6100,
    ("InVS15", 3): 6200,
    ("LH10", 2): 7100,
    ("LH10", 3): 7200,
    ("SFHH", 2): 8100,
    ("SFHH", 3): 8200,
    ("Thiers13", 2): 9100,
    ("Thiers13", 3): 9200,
}


def main():
    dataset_path = DATA_DIR / DATASET_FILES[args.dataset]
    out = RESULTS_DIR / f"part3_{args.dataset}_D{args.max_dimension}_full_sweep_{PROFILE}.pkl"
    if out.exists():
        print(f"checkpoint exists: {out}")
        return

    clique_realizations = load_sociopatterns_realizations(dataset_path)
    all_results = []
    realization_payloads = []
    lambda3_target = 0.0 if args.max_dimension == 2 else LAMBDA3_TARGET
    base_seed = BASE_SEEDS[(args.dataset, args.max_dimension)]

    for realization_index in range(len(clique_realizations)):
        print(f"dataset={args.dataset} D={args.max_dimension} realization={realization_index}")
        complex_data = import_sociopatterns_complex(
            dataset_path,
            realization=realization_index,
            max_dimension=args.max_dimension,
            seed=5,
        )
        results = run_prevalence_scan_torch_higher_order(
            complex_data,
            lambda1s=LAMBDA1S,
            lambda2_target=LAMBDA2_TARGET,
            lambda3_target=lambda3_target,
            seed_pct=SEED_PCT,
            t_max=T_MAX,
            mu=MU,
            n_sims=N_SIMS,
            base_seed=base_seed + realization_index * 100,
            device=args.device,
        )
        summary = parse_results(results, cut=False)
        realization_payloads.append(
            {
                "realization": realization_index,
                "complex_data": complex_data,
                "summary": summary,
            }
        )
        all_results.extend(results)

    payload = {
        "dataset": args.dataset,
        "dataset_path": str(dataset_path),
        "dataset_note": DATASET_NOTES[args.dataset],
        "max_dimension": args.max_dimension,
        "lambda2_target": LAMBDA2_TARGET,
        "lambda3_target": lambda3_target,
        "seed_pct": SEED_PCT,
        "n_simulations_per_realization": N_SIMS,
        "n_realizations": len(clique_realizations),
        "lambda1s": LAMBDA1S.tolist(),
        "summary": parse_results(all_results, cut=False),
        "results": all_results,
        "realizations": realization_payloads,
        "sem_caption": "Error bars indicate standard errors across all realization-by-simulation runs in the full dataset sweep.",
    }
    save_pickle(out, payload)
    print(out)


if __name__ == "__main__":
    main()
