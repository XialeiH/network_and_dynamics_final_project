from pathlib import Path
import json
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_import import import_sociopatterns_complex
from core.go_beyond_results import parse_results
from core.go_beyond_experiments import save_pickle
from core.go_beyond_torch_higher_order import run_prevalence_scan_torch_higher_order


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


def main():
    search_json = RESULTS_DIR / f"part3_empirical_tetrahedron_search_{PROFILE}.json"
    payload = json.loads(search_json.read_text())

    if not payload["has_positive_k3"]:
        diagnostic_path = RESULTS_DIR / f"part3_empirical_diagnostic_{PROFILE}.json"
        diagnostic_path.write_text(
            json.dumps(
                {
                    "status": "no_positive_k3_found",
                    "message": "No preprocessed empirical import contains a nonzero tetrahedron participation average. "
                    "The D=3 empirical channel is structurally inactive in the available files.",
                },
                indent=2,
            )
        )
        print(diagnostic_path)
        return

    best = payload["best_positive"]
    dataset_path = ROOT.parent / "Data" / "Sociopatterns" / "thr_data_random" / best["file_name"]
    realization_index = int(best["realization_index"])
    empirical_d2 = import_sociopatterns_complex(dataset_path, realization=realization_index, max_dimension=2, seed=0)
    empirical_d3 = import_sociopatterns_complex(dataset_path, realization=realization_index, max_dimension=3, seed=0)

    runs = {}
    for idx, (label, complex_data, lambda3_target) in enumerate(
        [("Imported D=2", empirical_d2, 0.0), ("Imported D=3", empirical_d3, LAMBDA3_TARGET)]
    ):
        results = run_prevalence_scan_torch_higher_order(
            complex_data,
            lambda1s=LAMBDA1S,
            lambda2_target=LAMBDA2_TARGET,
            lambda3_target=lambda3_target,
            seed_pct=SEED_PCT,
            t_max=T_MAX,
            mu=MU,
            n_sims=N_SIMS,
            base_seed=17100 + idx * 100,
            device="cuda",
        )
        runs[label] = {
            "complex_data": complex_data,
            "results": results,
            "summary": parse_results(results, cut=False),
        }

    out = RESULTS_DIR / f"part3_empirical_best_d3_comparison_{PROFILE}.pkl"
    save_pickle(
        out,
        {
            "best_positive": best,
            "lambda1s": LAMBDA1S.tolist(),
            "lambda2_target": LAMBDA2_TARGET,
            "lambda3_target": LAMBDA3_TARGET,
            "runs": runs,
            "sem_caption": "Error bars indicate standard errors across 80 independent Monte Carlo runs.",
        },
    )
    print(out)


if __name__ == "__main__":
    main()
