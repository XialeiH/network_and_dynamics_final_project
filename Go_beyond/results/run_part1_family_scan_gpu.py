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

from core.go_beyond_generators import generate_family_complex
from core.go_beyond_results import parse_results
from core.go_beyond_experiments import save_pickle
from core.go_beyond_torch_d2 import run_prevalence_scan_torch_d2


parser = ArgumentParser()
parser.add_argument("--family", required=True, choices=["er", "scale_free", "small_world"])
parser.add_argument("--lambda2", type=float, required=True)
parser.add_argument("--seed-pct", type=float, required=True)
parser.add_argument("--device", default="cuda")
args = parser.parse_args()

PROFILE = "production"
N = 2000
MU = 0.05
T_MAX = 4000
N_SIMS = 80
LAMBDA1S = np.linspace(0.2, 2.2, 30)
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

generator_seed_map = {"er": 11, "scale_free": 12, "small_world": 13}
base_seed_map = {
    ("er", 0.8, 5.0): 1100,
    ("scale_free", 0.8, 5.0): 1200,
    ("small_world", 0.8, 5.0): 1300,
    ("er", 2.5, 1.0): 2100,
    ("scale_free", 2.5, 1.0): 2200,
    ("small_world", 2.5, 1.0): 2300,
    ("er", 2.5, 40.0): 3100,
    ("scale_free", 2.5, 40.0): 3200,
    ("small_world", 2.5, 40.0): 3300,
}


def main():
    calibration_path = RESULTS_DIR / f"part1_calibration_{PROFILE}.json"
    calibration = json.loads(calibration_path.read_text())
    chosen = calibration["families"][args.family]["chosen"]
    generator_mode = chosen["generator_mode"]
    params = chosen["params"]

    seed_pct_label = str(int(args.seed_pct)) if float(args.seed_pct).is_integer() else str(args.seed_pct).replace(".", "p")
    lambda2_label = str(args.lambda2).replace(".", "p")
    out = RESULTS_DIR / f"part1_{args.family}_lambda2_{lambda2_label}_seed_{seed_pct_label}_{PROFILE}_checkpoint.pkl"
    if out.exists():
        print(f"checkpoint exists: {out}")
        return

    complex_data = generate_family_complex(
        family=args.family,
        mode=generator_mode,
        n_nodes=N,
        max_dimension=2,
        seed=generator_seed_map[args.family],
        **params,
    )
    results = run_prevalence_scan_torch_d2(
        complex_data,
        lambda1s=LAMBDA1S,
        lambda2_target=args.lambda2,
        seed_pct=args.seed_pct,
        t_max=T_MAX,
        mu=MU,
        n_sims=N_SIMS,
        base_seed=base_seed_map[(args.family, float(args.lambda2), float(args.seed_pct))],
        device=args.device,
    )
    summary = parse_results(results, cut=False)
    payload = {
        "complex_data": complex_data,
        "results": results,
        "summary": summary,
        "family": args.family,
        "comparison_mode": "calibrated_controlled",
        "generator_mode": generator_mode,
        "generator_params": params,
        "lambda2_target": args.lambda2,
        "seed_pct": args.seed_pct,
        "sem_caption": "Error bars indicate standard errors across 80 independent Monte Carlo runs.",
    }
    save_pickle(out, payload)
    print(out)


if __name__ == "__main__":
    main()
