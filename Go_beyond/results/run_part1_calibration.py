from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_calibration import calibrate_part1_generators


PROFILE = "production"
N = 2000
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    calibration = calibrate_part1_generators(n_nodes=N, target_k1=16.0, target_k2=4.0, n_trials=8)
    calibration["profile"] = PROFILE
    calibration["n_nodes"] = N
    out = RESULTS_DIR / f"part1_calibration_{PROFILE}.json"
    out.write_text(json.dumps(calibration, indent=2))
    print(out)


if __name__ == "__main__":
    main()
