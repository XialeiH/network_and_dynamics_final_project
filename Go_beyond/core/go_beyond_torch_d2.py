from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import numpy as np


@dataclass
class TorchD2Complex:
    adjacency: "torch.Tensor"
    triangles: "torch.Tensor"
    avg_k1: float
    avg_k2: float
    n_nodes: int
    device: str


def _require_torch():
    import torch

    return torch


def build_torch_d2_complex(complex_data, device: str = "cuda") -> TorchD2Complex:
    torch = _require_torch()

    node_neighbors_dict = complex_data["node_neighbors_dict"]
    triangles_list = complex_data["triangles_list"]
    stats = complex_data["stats"]
    nodes = sorted(node_neighbors_dict.keys())
    index = {node: idx for idx, node in enumerate(nodes)}
    n_nodes = len(nodes)

    adjacency = torch.zeros((n_nodes, n_nodes), dtype=torch.float32, device=device)
    for node in nodes:
        src = index[node]
        for nn in node_neighbors_dict[node]:
            adjacency[src, index[nn]] = 1.0

    if triangles_list:
        triangles = torch.tensor(
            [[index[a], index[b], index[c]] for a, b, c in triangles_list],
            dtype=torch.long,
            device=device,
        )
    else:
        triangles = torch.empty((0, 3), dtype=torch.long, device=device)

    return TorchD2Complex(
        adjacency=adjacency,
        triangles=triangles,
        avg_k1=float(stats["avg_k1"]),
        avg_k2=float(stats["avg_k2"]),
        n_nodes=n_nodes,
        device=device,
    )


def _sample_initial_masks(
    n_sims: int,
    n_nodes: int,
    seed_pct: float,
    base_seed: int,
    device: str,
):
    torch = _require_torch()
    n_initial = min(int(seed_pct * n_nodes / 100.0), n_nodes)
    masks = torch.zeros((n_sims, n_nodes), dtype=torch.bool, device=device)
    if n_initial <= 0:
        return masks

    gen = torch.Generator(device=device)
    for sim_idx in range(n_sims):
        gen.manual_seed(base_seed + sim_idx)
        order = torch.randperm(n_nodes, generator=gen, device=device)
        masks[sim_idx, order[:n_initial]] = True
    return masks


def _triangle_support_counts(infected: "torch.Tensor", triangles: "torch.Tensor", n_nodes: int):
    torch = _require_torch()
    batch = infected.shape[0]
    if triangles.numel() == 0:
        return torch.zeros((batch, n_nodes), dtype=torch.int32, device=infected.device)

    tri_state = infected[:, triangles]  # [B, T, 3]
    infected_counts = tri_state.sum(dim=-1)
    active = infected_counts == 2
    susceptible = (~tri_state) & active.unsqueeze(-1)
    support = torch.zeros((batch, n_nodes), dtype=torch.int32, device=infected.device)
    for pos in range(3):
        node_ids = triangles[:, pos].unsqueeze(0).expand(batch, -1)
        support.scatter_add_(1, node_ids, susceptible[:, :, pos].to(torch.int32))
    return support


def _stationary_rho_from_history(count_history: "torch.Tensor", n_nodes: int, last_k_values: int = 100):
    torch = _require_torch()
    if count_history.numel() == 0:
        return torch.zeros((0,), dtype=torch.float32)

    final_counts = count_history[-1]
    tail = count_history[-min(last_k_values, count_history.shape[0]) :].float() / max(n_nodes, 1)
    avg_tail = tail.mean(dim=0)

    rho = avg_tail.clone()
    rho = torch.where(final_counts == n_nodes, torch.ones_like(rho), rho)
    rho = torch.where(final_counts == 0, torch.zeros_like(rho), rho)
    return rho


def run_prevalence_scan_torch_d2(
    complex_data,
    lambda1s,
    lambda2_target,
    seed_pct=1.0,
    t_max=1500,
    mu=0.05,
    n_sims=8,
    base_seed=12345,
    device="cuda",
):
    torch = _require_torch()

    torch_complex = build_torch_d2_complex(complex_data, device=device)
    beta1s = (
        mu / torch_complex.avg_k1 * np.array(lambda1s, dtype=float)
        if torch_complex.avg_k1 > 0
        else np.zeros_like(lambda1s, dtype=float)
    )
    beta2 = mu / torch_complex.avg_k2 * lambda2_target if torch_complex.avg_k2 > 0 else 0.0

    initial_masks = _sample_initial_masks(
        n_sims=n_sims,
        n_nodes=torch_complex.n_nodes,
        seed_pct=seed_pct,
        base_seed=base_seed,
        device=device,
    )

    results = []
    for lambda_idx, beta1 in enumerate(beta1s):
        infected = initial_masks.clone()
        count_history: List["torch.Tensor"] = []
        pair_beta = float(beta1)

        gen = torch.Generator(device=device)
        gen.manual_seed(base_seed + 100000 + lambda_idx)

        for _ in range(t_max + 1):
            infected_float = infected.float()
            infected_neighbor_counts = infected_float @ torch_complex.adjacency
            p_pair = 1.0 - torch.pow(1.0 - pair_beta, infected_neighbor_counts)

            tri_support = _triangle_support_counts(infected, torch_complex.triangles, torch_complex.n_nodes)
            p_tri = 1.0 - torch.pow(1.0 - beta2, tri_support.float())

            p_infect = 1.0 - (1.0 - p_pair) * (1.0 - p_tri)
            susceptible = ~infected
            infect_draw = torch.rand((n_sims, torch_complex.n_nodes), generator=gen, device=device)
            new_infected = susceptible & (infect_draw < p_infect)

            recover_draw = torch.rand((n_sims, torch_complex.n_nodes), generator=gen, device=device)
            recoverable = infected & (~new_infected)
            new_recovered = recoverable & (recover_draw < mu)

            infected = (infected | new_infected) & (~new_recovered)
            count_history.append(infected.sum(dim=1))

            if bool(((infected.sum(dim=1) == 0) | (infected.sum(dim=1) == torch_complex.n_nodes)).all()):
                break

        history_tensor = torch.stack(count_history, dim=0) if count_history else torch.empty((0, n_sims), device=device)
        rhos = _stationary_rho_from_history(history_tensor, torch_complex.n_nodes).detach().cpu().numpy()
        for sim_idx, rho in enumerate(rhos):
            if len(results) <= sim_idx:
                results.append(
                    {
                        "rhos": [],
                        "avg_k1": torch_complex.avg_k1,
                        "avg_k2": torch_complex.avg_k2,
                        "avg_k3": 0.0,
                        "seed_pct": seed_pct,
                        "mu": mu,
                        "lambda2_target": lambda2_target,
                        "lambda3_target": 0.0,
                        "cut": False,
                    }
                )
            results[sim_idx]["rhos"].append(float(rho))
    return results
