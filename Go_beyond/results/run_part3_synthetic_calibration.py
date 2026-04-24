from pathlib import Path
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_calibration_d3 import calibrate_part3_synthetic_generator


PROFILE = "production"
N = 2000
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    calibration = calibrate_part3_synthetic_generator(n_nodes=N)
    json_path = RESULTS_DIR / f"part3_synthetic_calibration_{PROFILE}.json"
    csv_path = RESULTS_DIR / f"part3_synthetic_calibration_table_{PROFILE}.csv"
    json_path.write_text(json.dumps(calibration, indent=2))

    with csv_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["k1_input", "k2_input", "k3_input", "mean_k1", "mean_k2", "mean_k3", "score"])
        for row in calibration["candidates"]:
            writer.writerow(
                [
                    row["params"]["k1"],
                    row["params"]["k2"],
                    row["params"]["k3"],
                    row["mean_k1"],
                    row["mean_k2"],
                    row["mean_k3"],
                    row["score"],
                ]
            )

    print(json_path)
    print(csv_path)


if __name__ == "__main__":
    main()
