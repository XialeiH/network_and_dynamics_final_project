# Go Beyond

This folder contains a self-contained extension of the original simplagion project.

It keeps all new code, notebooks, results, and figures inside `Go_beyond/` and does not modify the replication code outside this folder.

## Layout

- `core/`: local higher-order model, generators, import helpers, result parsing, plotting style
- `notebooks/`: experiment notebooks for the two go-beyond studies
- `results/`: saved experiment payloads
- `figures/`: saved plots
- `verify_go_beyond.py`: quick local verification script

## Studies

1. `network_structures_study.ipynb`
   - D=2 only
   - compares ER/RSC, scale-free, and small-world
   - includes controlled and native parameter runs
   - set `PROFILE = 'smoke_test'` or `PROFILE = 'production'` near the top

2. `d3_tetrahedra_study.ipynb`
   - true tetrahedron contagion
   - synthetic D=3 example
   - empirical/import-ready example from the external Sociopatterns data
   - set `PROFILE = 'smoke_test'` or `PROFILE = 'production'` near the top

## Quick verification

Run:

```bash
python3 Go_beyond/verify_go_beyond.py
```

This performs smoke checks on:

- D=2 compatibility inside `Go_beyond/`
- tetrahedron triggering logic
- generator output validity
- empirical D=3 import preserving tetrahedra
