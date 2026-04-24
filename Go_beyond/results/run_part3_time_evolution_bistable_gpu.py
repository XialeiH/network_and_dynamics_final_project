from pathlib import Path
import json
import sys

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_analytic import select_representative_bistable_lambda1
from core.go_beyond_experiments import save_pickle
from core.go_beyond_generators import generate_family_complex
from core.go_beyond_torch_higher_order import run_time_evolution_scan_torch_higher_order


PROFILE = "production"
N = 2000
MU = 0.05
T_MAX = 4000
LAMBDA2_TARGET = 1.2
LAMBDA3_TARGET = 1.2
RHO0_LIST = [0.02, 0.05, 0.10, 0.20, 0.35, 0.50, 0.70, 0.90]
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


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
        seed=31,
        **params,
    )


def main():
    out = RESULTS_DIR / f"d3_time_evolution_bistable_lambda2_1p2_lambda3_1p2_{PROFILE}.pkl"
    if out.exists():
        print(f"checkpoint exists: {out}")
        return

    analytic_choice = select_representative_bistable_lambda1(LAMBDA2_TARGET, LAMBDA3_TARGET)
    complex_data = synthetic_complex()
    histories = run_time_evolution_scan_torch_higher_order(
        complex_data,
        lambda_target=analytic_choice["lambda1"],
        lambda2_target=LAMBDA2_TARGET,
        lambda3_target=LAMBDA3_TARGET,
        rho0_list=RHO0_LIST,
        t_max=T_MAX,
        mu=MU,
        base_seed=15100,
        device="cuda",
    )
    payload = {
        "complex_data": complex_data,
        "histories": histories,
        "lambda1": analytic_choice["lambda1"],
        "lambda1_window": analytic_choice["window"],
        "unstable_root": analytic_choice["unstable_root"],
        "stable_endemic_root": analytic_choice["stable_endemic_root"],
        "lambda2_target": LAMBDA2_TARGET,
        "lambda3_target": LAMBDA3_TARGET,
        "rho0_list": RHO0_LIST,
    }
    save_pickle(out, payload)
    print(out)


if __name__ == "__main__":
    main()
