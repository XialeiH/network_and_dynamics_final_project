from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .go_beyond_generators import generate_family_complex


TARGET_K1 = 16.0
TARGET_K2 = 4.0
TARGET_K3 = 1.5


@dataclass(frozen=True)
class D3CalibrationChoice:
    params: Dict[str, float]
    mean_k1: float
    mean_k2: float
    mean_k3: float
    score: float


def _score(mean_k1, mean_k2, mean_k3, target_k1=TARGET_K1, target_k2=TARGET_K2, target_k3=TARGET_K3):
    return abs(mean_k1 - target_k1) + 2.0 * abs(mean_k2 - target_k2) + 2.0 * abs(mean_k3 - target_k3)


def _summarize_records(records):
    mean_k1 = sum(record["avg_k1"] for record in records) / max(len(records), 1)
    mean_k2 = sum(record["avg_k2"] for record in records) / max(len(records), 1)
    mean_k3 = sum(record["avg_k3"] for record in records) / max(len(records), 1)
    return mean_k1, mean_k2, mean_k3


def calibrate_part3_synthetic_generator(
    n_nodes: int,
    target_k1: float = TARGET_K1,
    target_k2: float = TARGET_K2,
    target_k3: float = TARGET_K3,
    n_trials: int = 5,
):
    candidate_inputs = [
        {"k1": k1, "k2": k2, "k3": k3}
        for k1 in [15.0, 16.0, 17.0]
        for k2 in [1.5, 2.0, 2.5, 3.0]
        for k3 in [1.25, 1.5, 1.75]
    ]

    calibration_log = {
        "family": "er",
        "generator_mode": "controlled",
        "target_k1": target_k1,
        "target_k2": target_k2,
        "target_k3": target_k3,
        "n_trials": n_trials,
        "candidates": [],
        "chosen": None,
    }

    best_choice = None
    seed_base = 5510
    for candidate_idx, params in enumerate(candidate_inputs):
        records: List[Dict[str, float]] = []
        for trial_idx in range(n_trials):
            complex_data = generate_family_complex(
                family="er",
                mode="controlled",
                n_nodes=n_nodes,
                max_dimension=3,
                seed=seed_base + candidate_idx * 100 + trial_idx,
                **params,
            )
            stats = complex_data["stats"]
            records.append(
                {
                    "avg_k1": float(stats["avg_k1"]),
                    "avg_k2": float(stats["avg_k2"]),
                    "avg_k3": float(stats["avg_k3"]),
                }
            )
        mean_k1, mean_k2, mean_k3 = _summarize_records(records)
        score = _score(mean_k1, mean_k2, mean_k3, target_k1, target_k2, target_k3)
        row = {
            "params": dict(params),
            "mean_k1": mean_k1,
            "mean_k2": mean_k2,
            "mean_k3": mean_k3,
            "score": score,
        }
        calibration_log["candidates"].append(row)
        choice = D3CalibrationChoice(
            params=dict(params),
            mean_k1=mean_k1,
            mean_k2=mean_k2,
            mean_k3=mean_k3,
            score=score,
        )
        if best_choice is None or choice.score < best_choice.score:
            best_choice = choice

    calibration_log["chosen"] = {
        "params": dict(best_choice.params),
        "mean_k1": best_choice.mean_k1,
        "mean_k2": best_choice.mean_k2,
        "mean_k3": best_choice.mean_k3,
        "score": best_choice.score,
    }
    return calibration_log
