import json
import random
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx

from .go_beyond_generators import summarize_complex


def create_complex_from_cliques(cliques: Sequence[Sequence[int]], max_dimension: int = 3):
    graph = nx.Graph()
    triangles = set()
    tetrahedra = set()

    for clique in cliques:
        clique = tuple(sorted(map(int, clique)))
        if len(clique) < 2:
            continue
        for i, j in combinations(clique, 2):
            graph.add_edge(i, j)
        if max_dimension >= 2 and len(clique) >= 3:
            for tri in combinations(clique, 3):
                triangles.add(tuple(sorted(tri)))
        if max_dimension >= 3 and len(clique) >= 4:
            for tet in combinations(clique, 4):
                tetrahedra.add(tuple(sorted(tet)))

    node_neighbors_dict = {
        int(node): tuple(sorted(int(nn) for nn in graph.neighbors(node)))
        for node in sorted(graph.nodes())
    }
    triangles_list = [list(tri) for tri in sorted(triangles)]
    tetrahedra_list = [list(tet) for tet in sorted(tetrahedra)]
    stats = summarize_complex(node_neighbors_dict, triangles_list, tetrahedra_list)
    return {
        "node_neighbors_dict": node_neighbors_dict,
        "triangles_list": triangles_list,
        "tetrahedra_list": tetrahedra_list,
        "stats": stats,
    }


def import_sociopatterns_complex(
    dataset_path,
    realization="random",
    max_dimension: int = 3,
    seed: int = 0,
):
    dataset_path = Path(dataset_path)
    with dataset_path.open("r") as handle:
        clique_realizations = json.load(handle)

    if not clique_realizations:
        raise ValueError(f"No clique realizations found in {dataset_path}")

    if realization == "random":
        rng = random.Random(seed)
        selected = clique_realizations[rng.randrange(len(clique_realizations))]
        realization_index = "random"
    else:
        realization_index = int(realization)
        selected = clique_realizations[realization_index]

    complex_data = create_complex_from_cliques(selected, max_dimension=max_dimension)
    complex_data["dataset_path"] = str(dataset_path)
    complex_data["realization"] = realization_index
    return complex_data

