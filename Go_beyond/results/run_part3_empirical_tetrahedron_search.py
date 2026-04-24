from pathlib import Path
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.go_beyond_import import import_sociopatterns_complex, load_sociopatterns_realizations


PROFILE = "production"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = ROOT.parent / "Data" / "Sociopatterns" / "thr_data_random"

DATASET_FAMILY = {
    "InVS15": "workplace",
    "InVS13": "workplace",
    "LH10": "conference",
    "SFHH": "hospital",
    "Thiers13": "high_school",
    "LyonSchool": "high_school",
}


def infer_dataset_name(filename: str):
    stem = filename.replace(".json", "")
    return stem.split("_cliques_")[-1]


def main():
    rows = []
    for dataset_path in sorted(DATA_DIR.glob("random_*_cliques_*.json")):
        realizations = load_sociopatterns_realizations(dataset_path)
        dataset_name = infer_dataset_name(dataset_path.name)
        dataset_family = DATASET_FAMILY.get(dataset_name, "unknown")
        for realization_index in range(len(realizations)):
            complex_data = import_sociopatterns_complex(
                dataset_path,
                realization=realization_index,
                max_dimension=3,
                seed=0,
            )
            stats = complex_data["stats"]
            rows.append(
                {
                    "file_name": dataset_path.name,
                    "dataset_name": dataset_name,
                    "dataset_family": dataset_family,
                    "realization_index": realization_index,
                    "N": int(stats["N"]),
                    "avg_k1": float(stats["avg_k1"]),
                    "avg_k2": float(stats["avg_k2"]),
                    "avg_k3": float(stats.get("avg_k3", 0.0)),
                }
            )

    rows.sort(key=lambda row: (row["avg_k3"], row["avg_k2"], row["N"]), reverse=True)
    best_positive = next((row for row in rows if row["avg_k3"] > 0.0), None)

    csv_path = RESULTS_DIR / f"part3_empirical_tetrahedron_search_{PROFILE}.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["file_name", "dataset_name", "dataset_family", "realization_index", "N", "avg_k1", "avg_k2", "avg_k3"],
        )
        writer.writeheader()
        writer.writerows(rows)

    json_path = RESULTS_DIR / f"part3_empirical_tetrahedron_search_{PROFILE}.json"
    json_path.write_text(
        json.dumps(
            {
                "n_rows": len(rows),
                "has_positive_k3": best_positive is not None,
                "best_positive": best_positive,
            },
            indent=2,
        )
    )
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()
