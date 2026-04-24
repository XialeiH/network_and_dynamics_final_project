from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .go_beyond_generators import generate_family_complex


TARGET_K1 = 16.0
TARGET_K2 = 4.0


@dataclass(frozen=True)
class CalibrationChoice:
    family: str
    generator_mode: str
    params: Dict[str, float]
    mean_k1: float
    mean_k2: float
    score: float


def _score(mean_k1, mean_k2, target_k1=TARGET_K1, target_k2=TARGET_K2):
    return abs(mean_k1 - target_k1) + 2.0 * abs(mean_k2 - target_k2)


def _summarize_records(records):
    mean_k1 = sum(record["avg_k1"] for record in records) / max(len(records), 1)
    mean_k2 = sum(record["avg_k2"] for record in records) / max(len(records), 1)
    return mean_k1, mean_k2


def calibrate_part1_generators(
    n_nodes: int,
    target_k1: float = TARGET_K1,
    target_k2: float = TARGET_K2,
    n_trials: int = 8,
):
    calibration_log = {
        "target_k1": target_k1,
        "target_k2": target_k2,
        "n_trials": n_trials,
        "families": {},
    }

    er_complex = generate_family_complex(
        family="er",
        mode="controlled",
        n_nodes=n_nodes,
        max_dimension=2,
        seed=11,
        k1=target_k1,
        k2=target_k2,
    )
    er_choice = CalibrationChoice(
        family="er",
        generator_mode="controlled",
        params={"k1": target_k1, "k2": target_k2},
        mean_k1=float(er_complex["stats"]["avg_k1"]),
        mean_k2=float(er_complex["stats"]["avg_k2"]),
        score=_score(er_complex["stats"]["avg_k1"], er_complex["stats"]["avg_k2"], target_k1, target_k2),
    )
    calibration_log["families"]["er"] = {
        "candidates": [
            {
                "params": dict(er_choice.params),
                "mean_k1": er_choice.mean_k1,
                "mean_k2": er_choice.mean_k2,
                "score": er_choice.score,
            }
        ],
        "chosen": {
            "generator_mode": er_choice.generator_mode,
            "params": dict(er_choice.params),
            "mean_k1": er_choice.mean_k1,
            "mean_k2": er_choice.mean_k2,
            "score": er_choice.score,
        },
    }

    sf_candidates = [{"m": m, "triangle_factor": 4.0} for m in [4, 5, 6, 7]]
    sw_candidates = [
        {"k_nearest": k_nearest, "rewiring_prob": rewiring_prob, "triangle_factor": 4.0}
        for k_nearest in [10, 12, 14, 16]
        for rewiring_prob in [0.10, 0.12]
    ]

    for family, candidates, seed_base in [
        ("scale_free", sf_candidates, 3010),
        ("small_world", sw_candidates, 4010),
    ]:
        candidate_rows = []
        best_choice = None
        for candidate_idx, params in enumerate(candidates):
            records: List[Dict[str, float]] = []
            for trial_idx in range(n_trials):
                complex_data = generate_family_complex(
                    family=family,
                    mode="native",
                    n_nodes=n_nodes,
                    max_dimension=2,
                    seed=seed_base + candidate_idx * 100 + trial_idx,
                    **params,
                )
                stats = complex_data["stats"]
                records.append({"avg_k1": float(stats["avg_k1"]), "avg_k2": float(stats["avg_k2"])})
            mean_k1, mean_k2 = _summarize_records(records)
            score = _score(mean_k1, mean_k2, target_k1, target_k2)
            row = {
                "params": dict(params),
                "mean_k1": mean_k1,
                "mean_k2": mean_k2,
                "score": score,
            }
            candidate_rows.append(row)
            choice = CalibrationChoice(
                family=family,
                generator_mode="native",
                params=dict(params),
                mean_k1=mean_k1,
                mean_k2=mean_k2,
                score=score,
            )
            if best_choice is None or choice.score < best_choice.score:
                best_choice = choice

        calibration_log["families"][family] = {
            "candidates": candidate_rows,
            "chosen": {
                "generator_mode": best_choice.generator_mode,
                "params": dict(best_choice.params),
                "mean_k1": best_choice.mean_k1,
                "mean_k2": best_choice.mean_k2,
                "score": best_choice.score,
            },
        }

    return calibration_log
