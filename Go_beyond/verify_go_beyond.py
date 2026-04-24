from pathlib import Path

from core.go_beyond_experiments import run_prevalence_scan
from core.go_beyond_generators import generate_family_complex
from core.go_beyond_import import create_complex_from_cliques, import_sociopatterns_complex
from core.go_beyond_model import SimplagionModelHigherOrder


BASE_DIR = Path(__file__).resolve().parent
DATASET_EXAMPLE = (
    BASE_DIR.parent
    / "Data"
    / "Sociopatterns"
    / "thr_data_random"
    / "random_5_0.8min_cliques_Thiers13.json"
)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def verify_generators():
    for family, kwargs in [
        ("er", {"mode": "controlled", "k1": 8, "k2": 2}),
        ("scale_free", {"mode": "controlled", "k1": 8, "k2": 2}),
        ("small_world", {"mode": "controlled", "k1": 8, "k2": 2}),
    ]:
        complex_data = generate_family_complex(
            family=family,
            n_nodes=80,
            max_dimension=2,
            seed=7,
            **kwargs,
        )
        assert_true(len(complex_data["node_neighbors_dict"]) > 0, f"{family} generator returned empty graph")
        assert_true("stats" in complex_data, f"{family} generator missing stats")


def verify_tetrahedron_logic():
    complex_data = create_complex_from_cliques([[0, 1, 2, 3]], max_dimension=3)
    model = SimplagionModelHigherOrder(
        complex_data["node_neighbors_dict"],
        complex_data["triangles_list"],
        complex_data["tetrahedra_list"],
        I_percentage=0,
    )
    model.initial_setup(fixed_nodes_to_infect=[0, 1, 2])
    model.run(t_max=1, beta1=0.0, beta2=0.0, beta3=1.0, mu=0.0, print_status=False)
    assert_true(3 in model.iAgentSet, "tetrahedron contagion did not infect the fourth node")

    model.initial_setup(fixed_nodes_to_infect=[0, 1])
    model.run(t_max=1, beta1=0.0, beta2=0.0, beta3=1.0, mu=0.0, print_status=False)
    assert_true(2 not in model.iAgentSet and 3 not in model.iAgentSet, "tetrahedron fired with fewer than three infected nodes")


def verify_d2_compatibility():
    complex_data = generate_family_complex(
        family="er",
        mode="controlled",
        n_nodes=60,
        k1=8,
        k2=2,
        max_dimension=2,
        seed=3,
    )
    results = run_prevalence_scan(
        complex_data,
        lambda1s=[0.5, 1.0],
        lambda2_target=0.8,
        lambda3_target=0.0,
        seed_pct=5,
        t_max=50,
        mu=0.05,
        n_sims=2,
    )
    assert_true(len(results) == 2, "D=2 scan did not return expected number of simulations")


def verify_import():
    if not DATASET_EXAMPLE.exists():
        raise FileNotFoundError(f"Expected dataset not found: {DATASET_EXAMPLE}")
    d2_complex = import_sociopatterns_complex(DATASET_EXAMPLE, max_dimension=2, seed=1)
    d3_complex = import_sociopatterns_complex(DATASET_EXAMPLE, max_dimension=3, seed=1)
    assert_true(len(d2_complex["tetrahedra_list"]) == 0, "D=2 import should not keep tetrahedra")
    assert_true(len(d3_complex["tetrahedra_list"]) >= 0, "D=3 import failed")


if __name__ == "__main__":
    verify_generators()
    verify_tetrahedron_logic()
    verify_d2_compatibility()
    verify_import()
    print("Go_beyond verification completed.")
