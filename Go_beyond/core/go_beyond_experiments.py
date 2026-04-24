import pickle
import random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np

from .go_beyond_model import SimplagionModelHigherOrder


_PREVALENCE_CONTEXT = None
_TIME_EVOLUTION_CONTEXT = None


def _complex_stats(complex_data):
    stats = complex_data["stats"]
    return stats["avg_k1"], stats["avg_k2"], stats.get("avg_k3", 0.0)


def _build_result_row(rhos, avg_k1, avg_k2, avg_k3, seed_pct, mu, lambda2_target, lambda3_target, cut):
    return {
        "rhos": rhos,
        "avg_k1": avg_k1,
        "avg_k2": avg_k2,
        "avg_k3": avg_k3,
        "seed_pct": seed_pct,
        "mu": mu,
        "lambda2_target": lambda2_target,
        "lambda3_target": lambda3_target,
        "cut": cut,
    }


def _run_single_prevalence_sim(
    complex_data,
    beta1s,
    beta2,
    beta3,
    seed_pct,
    t_max,
    mu,
    avg_k1,
    avg_k2,
    avg_k3,
    lambda2_target,
    lambda3_target,
    cut,
    sim_seed,
):
    random.seed(sim_seed)
    np.random.seed(sim_seed % (2**32))
    model = SimplagionModelHigherOrder(
        complex_data["node_neighbors_dict"],
        complex_data["triangles_list"],
        complex_data["tetrahedra_list"],
        seed_pct,
    )
    rhos = []
    for beta1 in beta1s:
        model.reset()
        model.run(t_max, float(beta1), beta2, beta3, mu, print_status=False)
        rhos.append(model.get_stationary_rho(normed=True, last_k_values=100))
    return _build_result_row(rhos, avg_k1, avg_k2, avg_k3, seed_pct, mu, lambda2_target, lambda3_target, cut)


def _init_prevalence_worker(
    complex_data,
    beta1s,
    beta2,
    beta3,
    seed_pct,
    t_max,
    mu,
    avg_k1,
    avg_k2,
    avg_k3,
    lambda2_target,
    lambda3_target,
    cut,
):
    global _PREVALENCE_CONTEXT
    _PREVALENCE_CONTEXT = {
        "complex_data": complex_data,
        "beta1s": beta1s,
        "beta2": beta2,
        "beta3": beta3,
        "seed_pct": seed_pct,
        "t_max": t_max,
        "mu": mu,
        "avg_k1": avg_k1,
        "avg_k2": avg_k2,
        "avg_k3": avg_k3,
        "lambda2_target": lambda2_target,
        "lambda3_target": lambda3_target,
        "cut": cut,
    }


def _run_prevalence_worker(sim_seed):
    return _run_single_prevalence_sim(sim_seed=sim_seed, **_PREVALENCE_CONTEXT)


def _run_single_time_evolution(
    complex_data,
    beta1,
    beta2,
    beta3,
    rho0,
    t_max,
    mu,
    sim_seed,
):
    random.seed(sim_seed)
    np.random.seed(sim_seed % (2**32))
    model = SimplagionModelHigherOrder(
        complex_data["node_neighbors_dict"],
        complex_data["triangles_list"],
        complex_data["tetrahedra_list"],
        rho0 * 100.0,
    )
    infected_history = model.run(t_max, beta1, beta2, beta3, mu, print_status=False)
    return {"rho0": rho0, "history": np.array(infected_history) / max(model.N, 1)}


def _init_time_evolution_worker(complex_data, beta1, beta2, beta3, t_max, mu):
    global _TIME_EVOLUTION_CONTEXT
    _TIME_EVOLUTION_CONTEXT = {
        "complex_data": complex_data,
        "beta1": beta1,
        "beta2": beta2,
        "beta3": beta3,
        "t_max": t_max,
        "mu": mu,
    }


def _run_time_evolution_worker(task):
    rho0, sim_seed = task
    return _run_single_time_evolution(rho0=rho0, sim_seed=sim_seed, **_TIME_EVOLUTION_CONTEXT)


def run_prevalence_scan(
    complex_data,
    lambda1s,
    lambda2_target,
    lambda3_target=0.0,
    seed_pct=1.0,
    t_max=1500,
    mu=0.05,
    n_sims=8,
    n_workers=1,
    cut=False,
    base_seed=12345,
):
    avg_k1, avg_k2, avg_k3 = _complex_stats(complex_data)
    beta1s = mu / avg_k1 * np.array(lambda1s) if avg_k1 > 0 else np.zeros_like(lambda1s)
    beta2 = mu / avg_k2 * lambda2_target if avg_k2 > 0 else 0.0
    beta3 = mu / avg_k3 * lambda3_target if avg_k3 > 0 else 0.0

    sim_seeds = [base_seed + sim_idx for sim_idx in range(n_sims)]
    if n_workers <= 1 or n_sims <= 1:
        return [
            _run_single_prevalence_sim(
                complex_data=complex_data,
                beta1s=beta1s,
                beta2=beta2,
                beta3=beta3,
                seed_pct=seed_pct,
                t_max=t_max,
                mu=mu,
                avg_k1=avg_k1,
                avg_k2=avg_k2,
                avg_k3=avg_k3,
                lambda2_target=lambda2_target,
                lambda3_target=lambda3_target,
                cut=cut,
                sim_seed=sim_seed,
            )
            for sim_seed in sim_seeds
        ]

    max_workers = min(int(n_workers), int(n_sims))
    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=_init_prevalence_worker,
        initargs=(
            complex_data,
            beta1s,
            beta2,
            beta3,
            seed_pct,
            t_max,
            mu,
            avg_k1,
            avg_k2,
            avg_k3,
            lambda2_target,
            lambda3_target,
            cut,
        ),
    ) as executor:
        return list(executor.map(_run_prevalence_worker, sim_seeds))


def run_time_evolution_scan(
    complex_data,
    lambda_target,
    lambda2_target,
    lambda3_target,
    rho0_list,
    t_max=300,
    mu=0.05,
    n_workers=1,
    base_seed=22345,
):
    avg_k1, avg_k2, avg_k3 = _complex_stats(complex_data)
    beta1 = mu / avg_k1 * lambda_target if avg_k1 > 0 else 0.0
    beta2 = mu / avg_k2 * lambda2_target if avg_k2 > 0 else 0.0
    beta3 = mu / avg_k3 * lambda3_target if avg_k3 > 0 else 0.0

    tasks = [(rho0, base_seed + idx) for idx, rho0 in enumerate(rho0_list)]
    if n_workers <= 1 or len(tasks) <= 1:
        return [
            _run_single_time_evolution(
                complex_data=complex_data,
                beta1=beta1,
                beta2=beta2,
                beta3=beta3,
                rho0=rho0,
                t_max=t_max,
                mu=mu,
                sim_seed=sim_seed,
            )
            for rho0, sim_seed in tasks
        ]

    max_workers = min(int(n_workers), len(tasks))
    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=_init_time_evolution_worker,
        initargs=(complex_data, beta1, beta2, beta3, t_max, mu),
    ) as executor:
        return list(executor.map(_run_time_evolution_worker, tasks))


def save_pickle(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        pickle.dump(payload, handle)
