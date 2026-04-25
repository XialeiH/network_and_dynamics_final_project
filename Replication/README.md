# Replication

This folder reproduces Figures 2, 3, and 4 of Iacopini et al. (2019), "Simplicial models of social contagion," *Nature Communications* 10:2485.

## Layout

- `core/`: utility modules from the authors' original repository (used without modification)
- `notebooks/`: notebooks for each replication plot
- `figures/`: saved output figures

## Data

Place the SocioPatterns JSON files in `../Data/Sociopatterns/thr_data_random/`.
Files can be downloaded from https://github.com/iaciac/simplagion.

## Notebooks

1. `fig2_sociopatterns.py`
   - prevalence curves on four real-world SocioPatterns datasets
   - edit `DATASET` near the top to one of: `InVS15` | `SFHH` | `LH10` | `Thiers13`
   - run with `python fig2_sociopatterns.py`

2. `fig3a_RSC.ipynb`
   - prevalence curves on synthetic RSC with mean-field overlay
   - adapted from the authors' original `Simplagion on our RSC model.ipynb`, parameters unchanged

3. `fig3b_time_evolution.ipynb`
   - time evolution of infection density for different initial conditions
   - fixed parameters: `lambda=0.75`, `lambda_Delta=2.5`, 19 values of rho_0

4. `fig4_phase_diagram.ipynb`
   - full mean-field phase diagram, computed purely analytically
   - no simulation data required
   - includes both stable and unstable branches of Eq. (4), which the authors' code does not provide

