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
from core.go_beyond_torch_higher_order import run_prevalence_scan_torch_higher_order


parser = ArgumentParser()
parser.add_argument("--seed-pct", type=float, required=True, choices=[1.0, 40.0])
parser.add_argument("--device", default="cuda")
args = parser.parse_args()

PROFILE = "production"
N = 2000
MU = 0.05
T_MAX = 4000
N_SIMS = 80
LAMBDA1S = np.linspace(0.2, 2.2, 30)
LAMBDA2_TARGET = 1.2
LAMBDA3_TARGET = 1.2
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

GENERATOR_SEED = 31
BASE_SEEDS = {1.0: 11100, 40.0: 11200}


def synthetic_complex():
    calibration_path = RESULTS_DIR / f"part3_synthetic_calibration_{PROFILE}.json"
    if calibration_path.exists():
        calibration = json.loads(calibration_path.read_text())
        params = calibration["chosen"]["params"]
    else:
        params = {"k1": 16.0, "k2": 4.0, "k3": 1.5}
    return generate_family_complex(
        family="er",
        mode="controlled",
        n_nodes=N,
        max_dimension=3,
        seed=GENERATOR_SEED,
        **params,
    )


def main():
    seed_pct_label = str(int(args.seed_pct))
    out = RESULTS_DIR / f"d3_synthetic_bistability_lambda2_1p2_lambda3_1p2_seed_{seed_pct_label}_{PROFILE}.pkl"
    if out.exists():
        print(f"checkpoint exists: {out}")
        return

    complex_data = synthetic_complex()
    results = run_prevalence_scan_torch_higher_order(
        complex_data,
        lambda1s=LAMBDA1S,
        lambda2_target=LAMBDA2_TARGET,
        lambda3_target=LAMBDA3_TARGET,
        seed_pct=args.seed_pct,
        t_max=T_MAX,
        mu=MU,
        n_sims=N_SIMS,
        base_seed=BASE_SEEDS[float(args.seed_pct)],
        device=args.device,
    )
    summary = parse_results(results, cut=False)
    payload = {
        "complex_data": complex_data,
        "results": results,
        "summary": summary,
        "lambda1s": LAMBDA1S.tolist(),
        "lambda2_target": LAMBDA2_TARGET,
        "lambda3_target": LAMBDA3_TARGET,
        "seed_pct": args.seed_pct,
        "n_simulations": N_SIMS,
        "sem_caption": "Error bars indicate standard errors across 80 independent Monte Carlo runs.",
    }
    save_pickle(out, payload)
    print(out)


if __name__ == "__main__":
    main()
