from pathlib import Path
import argparse
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_experiments import run_prevalence_scan, save_pickle
from core.go_beyond_generators import generate_family_complex
from core.go_beyond_results import parse_results


parser = argparse.ArgumentParser()
parser.add_argument("--mode", required=True)
parser.add_argument("--family", required=True)
parser.add_argument("--workers", type=int, default=16)
args = parser.parse_args()

PROFILE = "production"
N = 2000
MU = 0.05
T_MAX = 4000
N_SIMS = 80
N_WORKERS = args.workers
LAMBDA1S = np.linspace(0.2, 2.2, 30)
LAMBDA2_TARGET = 0.8
SEED_PCT = 5
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SPECS = {
    "controlled": {
        "er": {"k1": 16, "k2": 4},
        "scale_free": {"k1": 16, "k2": 4},
        "small_world": {"k1": 16, "k2": 4},
    },
    "native": {
        "er": {"p1": 0.008, "p2": 0.00001},
        "scale_free": {"m": 8, "triangle_factor": 4.0},
        "small_world": {"k_nearest": 16, "rewiring_prob": 0.12, "triangle_factor": 4.0},
    },
}
SEED_MAP = {"controlled": 11, "native": 19}
BASE_SEED_MAP = {
    ("controlled", "er"): 1100,
    ("controlled", "scale_free"): 1200,
    ("controlled", "small_world"): 1300,
    ("native", "er"): 2100,
    ("native", "scale_free"): 2200,
    ("native", "small_world"): 2300,
}

checkpoint_path = RESULTS_DIR / f"{args.mode}_{args.family}_{PROFILE}_checkpoint.pkl"
if checkpoint_path.exists():
    print(f"checkpoint exists: {checkpoint_path}", flush=True)
    sys.exit(0)

print(f"building {args.mode}/{args.family}", flush=True)
complex_data = generate_family_complex(
    family=args.family,
    mode=args.mode,
    n_nodes=N,
    max_dimension=2,
    seed=SEED_MAP[args.mode],
    **SPECS[args.mode][args.family],
)
print(f"running prevalence scan for {args.mode}/{args.family} with {N_WORKERS} workers", flush=True)
results = run_prevalence_scan(
    complex_data,
    lambda1s=LAMBDA1S,
    lambda2_target=LAMBDA2_TARGET,
    seed_pct=SEED_PCT,
    t_max=T_MAX,
    mu=MU,
    n_sims=N_SIMS,
    n_workers=N_WORKERS,
    base_seed=BASE_SEED_MAP[(args.mode, args.family)],
)
summary = parse_results(results, cut=False)
payload = {"complex_data": complex_data, "results": results, "summary": summary}
save_pickle(checkpoint_path, payload)
print(f"finished {args.mode}/{args.family}", flush=True)
