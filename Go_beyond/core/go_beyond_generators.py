import math
import random
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import networkx as nx


def _ensure_connected_or_giant_component(graph: nx.Graph) -> nx.Graph:
    if graph.number_of_nodes() == 0:
        return graph
    if nx.is_connected(graph):
        return graph
    giant_nodes = max(nx.connected_components(graph), key=len)
    return graph.subgraph(giant_nodes).copy()


def _normalize_complex(
    graph: nx.Graph,
    triangles: Iterable[Sequence[int]],
    tetrahedra: Iterable[Sequence[int]],
) -> Dict[str, object]:
    triangles_set = {tuple(sorted(map(int, tri))) for tri in triangles}
    tetrahedra_set = {tuple(sorted(map(int, tet))) for tet in tetrahedra}

    graph = graph.copy()
    for triangle in triangles_set:
        for i, j in combinations(triangle, 2):
            graph.add_edge(i, j)
    for tetrahedron in tetrahedra_set:
        for i, j in combinations(tetrahedron, 2):
            graph.add_edge(i, j)
        for tri in combinations(tetrahedron, 3):
            triangles_set.add(tuple(sorted(tri)))

    graph = _ensure_connected_or_giant_component(graph)
    kept_nodes = set(graph.nodes())
    triangles_set = {tri for tri in triangles_set if set(tri).issubset(kept_nodes)}
    tetrahedra_set = {tet for tet in tetrahedra_set if set(tet).issubset(kept_nodes)}

    node_neighbors_dict = {
        int(node): tuple(sorted(int(nn) for nn in graph.neighbors(node)))
        for node in sorted(graph.nodes())
    }
    return {
        "node_neighbors_dict": node_neighbors_dict,
        "triangles_list": [list(tri) for tri in sorted(triangles_set)],
        "tetrahedra_list": [list(tet) for tet in sorted(tetrahedra_set)],
        "graph": graph,
    }


def summarize_complex(node_neighbors_dict, triangles_list, tetrahedra_list):
    if not node_neighbors_dict:
        return {"N": 0, "avg_k1": 0.0, "avg_k2": 0.0, "avg_k3": 0.0}
    n_nodes = len(node_neighbors_dict)
    avg_k1 = sum(len(v) for v in node_neighbors_dict.values()) / n_nodes
    tri_counts = {node: 0 for node in node_neighbors_dict}
    tet_counts = {node: 0 for node in node_neighbors_dict}
    for tri in triangles_list:
        for node in tri:
            tri_counts[node] += 1
    for tet in tetrahedra_list:
        for node in tet:
            tet_counts[node] += 1
    avg_k2 = sum(tri_counts.values()) / n_nodes
    avg_k3 = sum(tet_counts.values()) / n_nodes
    return {"N": n_nodes, "avg_k1": avg_k1, "avg_k2": avg_k2, "avg_k3": avg_k3}


def _triangle_target_count(n_nodes: int, k2: float) -> int:
    return max(0, int(round(k2 * n_nodes / 3.0)))


def _tetra_target_count(n_nodes: int, k3: float) -> int:
    return max(0, int(round(k3 * n_nodes / 4.0)))


def _choose_weighted_node(nodes: List[int], weights: List[float], rng: random.Random) -> int:
    return rng.choices(nodes, weights=weights, k=1)[0]


def _add_random_triangles(
    graph: nx.Graph,
    target_count: int,
    rng: random.Random,
    mode: str = "uniform",
    local_span: Optional[int] = None,
) -> List[Tuple[int, int, int]]:
    nodes = list(graph.nodes())
    if len(nodes) < 3 or target_count <= 0:
        return []

    triangles = set()
    degrees = [max(1, graph.degree(node)) for node in nodes]
    attempts = 0
    max_attempts = max(50 * target_count, 500)

    while len(triangles) < target_count and attempts < max_attempts:
        attempts += 1
        if mode == "preferential":
            anchor = _choose_weighted_node(nodes, degrees, rng)
            neighborhood = list(set(graph.neighbors(anchor)) | {anchor})
            if len(neighborhood) < 3:
                continue
            tri = tuple(sorted(rng.sample(neighborhood, 3)))
        elif mode == "local":
            anchor = rng.choice(nodes)
            span = max(2, local_span or max(2, len(nodes) // 20))
            candidates = sorted(
                {
                    ((anchor + offset) % len(nodes))
                    for offset in range(-span, span + 1)
                }
            )
            if len(candidates) < 3:
                continue
            tri = tuple(sorted(rng.sample(candidates, 3)))
        else:
            tri = tuple(sorted(rng.sample(nodes, 3)))
        triangles.add(tri)
    return sorted(triangles)


def _add_random_tetrahedra(
    graph: nx.Graph,
    target_count: int,
    rng: random.Random,
    mode: str = "uniform",
    local_span: Optional[int] = None,
) -> List[Tuple[int, int, int, int]]:
    nodes = list(graph.nodes())
    if len(nodes) < 4 or target_count <= 0:
        return []

    tetrahedra = set()
    degrees = [max(1, graph.degree(node)) for node in nodes]
    attempts = 0
    max_attempts = max(80 * target_count, 800)

    while len(tetrahedra) < target_count and attempts < max_attempts:
        attempts += 1
        if mode == "preferential":
            anchor = _choose_weighted_node(nodes, degrees, rng)
            neighborhood = list(set(graph.neighbors(anchor)) | {anchor})
            if len(neighborhood) < 4:
                continue
            tet = tuple(sorted(rng.sample(neighborhood, 4)))
        elif mode == "local":
            anchor = rng.choice(nodes)
            span = max(3, local_span or max(3, len(nodes) // 16))
            candidates = sorted(
                {
                    ((anchor + offset) % len(nodes))
                    for offset in range(-span, span + 1)
                }
            )
            if len(candidates) < 4:
                continue
            tet = tuple(sorted(rng.sample(candidates, 4)))
        else:
            tet = tuple(sorted(rng.sample(nodes, 4)))
        tetrahedra.add(tet)
    return sorted(tetrahedra)


def _safe_probability(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def get_er_probabilities_from_targets(n_nodes: int, k1: float, k2: float, k3: float = 0.0):
    denom3 = max((n_nodes - 1) * (n_nodes - 2) * (n_nodes - 3), 1)
    p3 = _safe_probability((6.0 * k3) / denom3)
    denom2 = max((n_nodes - 1) * (n_nodes - 2), 1)
    p2 = _safe_probability((2.0 * k2) / denom2)
    residual_k1 = max(0.0, k1 - 2.0 * k2 - 3.0 * k3)
    p1 = _safe_probability(residual_k1 / max(n_nodes - 1, 1))
    return p1, p2, p3


def generate_er_native(n_nodes: int, p1: float, p2: float, p3: float = 0.0, seed: Optional[int] = None):
    rng = random.Random(seed)
    graph = nx.fast_gnp_random_graph(n_nodes, _safe_probability(p1), seed=seed)
    graph = _ensure_connected_or_giant_component(graph)

    current_n = graph.number_of_nodes()
    tri_target = int(round(_safe_probability(p2) * math.comb(current_n, 3))) if current_n >= 3 else 0
    tet_target = int(round(_safe_probability(p3) * math.comb(current_n, 4))) if current_n >= 4 else 0
    triangles = _add_random_triangles(graph, tri_target, rng, mode="uniform")
    tetrahedra = _add_random_tetrahedra(graph, tet_target, rng, mode="uniform")

    return _normalize_complex(graph, triangles, tetrahedra)


def generate_er_controlled(n_nodes: int, k1: float, k2: float, k3: float = 0.0, seed: Optional[int] = None):
    p1, p2, p3 = get_er_probabilities_from_targets(n_nodes, k1, k2, k3)
    complex_data = generate_er_native(n_nodes, p1=p1, p2=p2, p3=p3, seed=seed)
    complex_data["generator_params"] = {"p1": p1, "p2": p2, "p3": p3}
    return complex_data


def generate_scale_free_native(
    n_nodes: int,
    m: int,
    triangle_factor: float = 1.0,
    tetra_factor: float = 0.0,
    seed: Optional[int] = None,
):
    rng = random.Random(seed)
    graph = nx.barabasi_albert_graph(n_nodes, max(1, int(m)), seed=seed)
    graph = _ensure_connected_or_giant_component(graph)
    tri_count = max(0, int(round(triangle_factor * graph.number_of_nodes() / 3.0)))
    tet_count = max(0, int(round(tetra_factor * graph.number_of_nodes() / 4.0)))
    triangles = _add_random_triangles(graph, tri_count, rng, mode="preferential")
    tetrahedra = _add_random_tetrahedra(graph, tet_count, rng, mode="preferential")
    return _normalize_complex(graph, triangles, tetrahedra)


def generate_scale_free_controlled(
    n_nodes: int,
    k1: float,
    k2: float,
    k3: float = 0.0,
    seed: Optional[int] = None,
):
    m = max(1, int(round(k1 / 2.0)))
    triangle_factor = max(k2, 0.0)
    tetra_factor = max(k3, 0.0)
    complex_data = generate_scale_free_native(
        n_nodes=n_nodes,
        m=m,
        triangle_factor=triangle_factor,
        tetra_factor=tetra_factor,
        seed=seed,
    )
    complex_data["generator_params"] = {
        "m": m,
        "triangle_factor": triangle_factor,
        "tetra_factor": tetra_factor,
    }
    return complex_data


def generate_small_world_native(
    n_nodes: int,
    k_nearest: int,
    rewiring_prob: float,
    triangle_factor: float = 1.0,
    tetra_factor: float = 0.0,
    seed: Optional[int] = None,
):
    rng = random.Random(seed)
    k_nearest = max(2, int(k_nearest))
    if k_nearest % 2 == 1:
        k_nearest += 1
    graph = nx.watts_strogatz_graph(
        n_nodes,
        min(k_nearest, max(2, n_nodes - (n_nodes % 2 == 0))),
        _safe_probability(rewiring_prob),
        seed=seed,
    )
    graph = _ensure_connected_or_giant_component(graph)
    tri_count = max(0, int(round(triangle_factor * graph.number_of_nodes() / 3.0)))
    tet_count = max(0, int(round(tetra_factor * graph.number_of_nodes() / 4.0)))
    local_span = max(3, k_nearest)
    triangles = _add_random_triangles(graph, tri_count, rng, mode="local", local_span=local_span)
    tetrahedra = _add_random_tetrahedra(graph, tet_count, rng, mode="local", local_span=local_span)
    return _normalize_complex(graph, triangles, tetrahedra)


def generate_small_world_controlled(
    n_nodes: int,
    k1: float,
    k2: float,
    k3: float = 0.0,
    seed: Optional[int] = None,
):
    k_nearest = max(2, int(round(k1)))
    if k_nearest % 2 == 1:
        k_nearest += 1
    rewiring_prob = 0.1
    triangle_factor = max(k2, 0.0)
    tetra_factor = max(k3, 0.0)
    complex_data = generate_small_world_native(
        n_nodes=n_nodes,
        k_nearest=k_nearest,
        rewiring_prob=rewiring_prob,
        triangle_factor=triangle_factor,
        tetra_factor=tetra_factor,
        seed=seed,
    )
    complex_data["generator_params"] = {
        "k_nearest": k_nearest,
        "rewiring_prob": rewiring_prob,
        "triangle_factor": triangle_factor,
        "tetra_factor": tetra_factor,
    }
    return complex_data


def generate_family_complex(
    family: str,
    mode: str,
    n_nodes: int,
    max_dimension: int = 2,
    seed: Optional[int] = None,
    **kwargs,
):
    family = family.lower()
    mode = mode.lower()
    k3 = kwargs.get("k3", 0.0) if max_dimension >= 3 else 0.0

    if family == "er":
        if mode == "controlled":
            complex_data = generate_er_controlled(
                n_nodes=n_nodes,
                k1=kwargs["k1"],
                k2=kwargs.get("k2", 0.0),
                k3=k3,
                seed=seed,
            )
        else:
            complex_data = generate_er_native(
                n_nodes=n_nodes,
                p1=kwargs["p1"],
                p2=kwargs.get("p2", 0.0),
                p3=kwargs.get("p3", 0.0) if max_dimension >= 3 else 0.0,
                seed=seed,
            )
            complex_data["generator_params"] = {
                "p1": kwargs["p1"],
                "p2": kwargs.get("p2", 0.0),
                "p3": kwargs.get("p3", 0.0) if max_dimension >= 3 else 0.0,
            }
    elif family == "scale_free":
        if mode == "controlled":
            complex_data = generate_scale_free_controlled(
                n_nodes=n_nodes,
                k1=kwargs["k1"],
                k2=kwargs.get("k2", 0.0),
                k3=k3,
                seed=seed,
            )
        else:
            complex_data = generate_scale_free_native(
                n_nodes=n_nodes,
                m=kwargs["m"],
                triangle_factor=kwargs.get("triangle_factor", 1.0),
                tetra_factor=kwargs.get("tetra_factor", 0.0) if max_dimension >= 3 else 0.0,
                seed=seed,
            )
            complex_data["generator_params"] = {
                "m": kwargs["m"],
                "triangle_factor": kwargs.get("triangle_factor", 1.0),
                "tetra_factor": kwargs.get("tetra_factor", 0.0) if max_dimension >= 3 else 0.0,
            }
    elif family == "small_world":
        if mode == "controlled":
            complex_data = generate_small_world_controlled(
                n_nodes=n_nodes,
                k1=kwargs["k1"],
                k2=kwargs.get("k2", 0.0),
                k3=k3,
                seed=seed,
            )
        else:
            complex_data = generate_small_world_native(
                n_nodes=n_nodes,
                k_nearest=kwargs["k_nearest"],
                rewiring_prob=kwargs["rewiring_prob"],
                triangle_factor=kwargs.get("triangle_factor", 1.0),
                tetra_factor=kwargs.get("tetra_factor", 0.0) if max_dimension >= 3 else 0.0,
                seed=seed,
            )
            complex_data["generator_params"] = {
                "k_nearest": kwargs["k_nearest"],
                "rewiring_prob": kwargs["rewiring_prob"],
                "triangle_factor": kwargs.get("triangle_factor", 1.0),
                "tetra_factor": kwargs.get("tetra_factor", 0.0) if max_dimension >= 3 else 0.0,
            }
    else:
        raise ValueError(f"Unknown family: {family}")

    if max_dimension < 3:
        complex_data["tetrahedra_list"] = []
    stats = summarize_complex(
        complex_data["node_neighbors_dict"],
        complex_data["triangles_list"],
        complex_data["tetrahedra_list"],
    )
    complex_data["stats"] = stats
    complex_data["family"] = family
    complex_data["mode"] = mode
    complex_data["max_dimension"] = max_dimension
    return complex_data
