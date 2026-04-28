# Network and Dynamics Final Project

This repository is an NYU Shanghai final project built on the codebase for the paper [*Simplicial Models of Social Contagion*](https://www.nature.com/articles/s41467-019-10431-6) by Iacopini, Petri, Barrat, and Latora.

The project has two main parts:

- `Replication/`: reproduction of the main results from the original paper
- `Go_beyond/`: extensions beyond the original paper, including topology variation, true `D=3` tetrahedron contagion, empirical full-dataset sweeps, and a heterogeneous-recovery study

## Project Structure

- [Replication](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication)
  - reproduces Figures 2, 3, and 4 of the original paper
  - keeps the replication workflow separated from the extension work
- [Go_beyond](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond)
  - contains all new code, notebooks, results, and figures for the project extensions
- [Data](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Data)
  - SocioPatterns-derived processed input files used by replication and empirical extension experiments
- root-level notebooks and utilities
  - the original upstream notebooks and helper files are kept for reference

## Replication

The replication component lives in [Replication](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication).

Main outputs:

- [Replication/figures/fig2_InVS15.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/figures/fig2_InVS15.png)
- [Replication/figures/fig2_LH10.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/figures/fig2_LH10.png)
- [Replication/figures/fig2_SFHH.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/figures/fig2_SFHH.png)
- [Replication/figures/fig2_Thiers13.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/figures/fig2_Thiers13.png)
- [Replication/figures/fig3a.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/figures/fig3a.png)
- [Replication/figures/fig3b_time_evolution.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/figures/fig3b_time_evolution.png)
- [Replication/figures/fig4_phase_diagram.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/figures/fig4_phase_diagram.png)

Main notebooks and scripts:

- [Replication/notebooks/fig2_sociopatterns.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/notebooks/fig2_sociopatterns.py)
- [Replication/notebooks/fig3a_RSC.ipynb](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/notebooks/fig3a_RSC.ipynb)
- [Replication/notebooks/fig3b_time_evolution.ipynb](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/notebooks/fig3b_time_evolution.ipynb)
- [Replication/notebooks/fig4_phase_diagram.ipynb](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Replication/notebooks/fig4_phase_diagram.ipynb)

## Go Beyond

The extension component lives in [Go_beyond](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond).

It is organized as:

- [Go_beyond/core](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core)
  - new simulation engines, generators, analytic helpers, import logic, calibration utilities, and plotting utilities
- [Go_beyond/notebooks](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/notebooks)
  - notebook entry points for the main extension studies
- [Go_beyond/results](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/results)
  - saved `.pkl`, `.json`, and `.csv` result files
- [Go_beyond/figures](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/figures)
  - generated plots used in the report

### Part 1: Different Network Structures

This study keeps the contagion model at `D=2` and changes the synthetic network family:

- ER / RSC-style baseline
- scale-free
- small-world

Final corrected outputs:

- [Go_beyond/figures/network_structures_controlled_calibrated_production.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/figures/network_structures_controlled_calibrated_production.png)
- [Go_beyond/figures/network_structures_calibrated_lambda2_2p5_production.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/figures/network_structures_calibrated_lambda2_2p5_production.png)
- [Go_beyond/results/part1_calibration_production.json](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/results/part1_calibration_production.json)
- [Go_beyond/results/part1_calibration_table_production.csv](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/results/part1_calibration_table_production.csv)

Main implementation files:

- [Go_beyond/core/go_beyond_generators.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_generators.py)
- [Go_beyond/core/go_beyond_experiments.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_experiments.py)
- [Go_beyond/core/go_beyond_torch_d2.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_torch_d2.py)
- [Go_beyond/core/go_beyond_calibration.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_calibration.py)

### Part 3: True D=3 Tetrahedron Contagion

This study extends the original model from `D=2` to true `D=3` contagion by adding tetrahedron-mediated infection.

Main outputs:

- [Go_beyond/figures/d3_synthetic_bistability_lambda2_1p2_lambda3_1p2_production.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/figures/d3_synthetic_bistability_lambda2_1p2_lambda3_1p2_production.png)
- [Go_beyond/figures/d3_time_evolution_bistable_lambda2_1p2_lambda3_1p2_production.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/figures/d3_time_evolution_bistable_lambda2_1p2_lambda3_1p2_production.png)
- [Go_beyond/figures/part3_empirical_full_sweep_production.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/figures/part3_empirical_full_sweep_production.png)
- [Go_beyond/results/part3_empirical_tetrahedron_search_production.csv](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/results/part3_empirical_tetrahedron_search_production.csv)
- [Go_beyond/results/part3_empirical_diagnostic_production.json](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/results/part3_empirical_diagnostic_production.json)

Main implementation files:

- [Go_beyond/core/go_beyond_model.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_model.py)
- [Go_beyond/core/go_beyond_analytic.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_analytic.py)
- [Go_beyond/core/go_beyond_torch_higher_order.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_torch_higher_order.py)
- [Go_beyond/core/go_beyond_import.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/go_beyond_import.py)

### Additional Study: Heterogeneous Recovery Rate

This study keeps the original RSC-style setting but relaxes the constant recovery-rate assumption.

Main outputs:

- [Go_beyond/notebooks/heterogeneous_mu_study.ipynb](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/notebooks/heterogeneous_mu_study.ipynb)
- [Go_beyond/figures/mu_updated_result.png](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/figures/mu_updated_result.png)
- [Go_beyond/core/utils_simplagion_on_RSC_heterogeneous_mu.py](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/core/utils_simplagion_on_RSC_heterogeneous_mu.py)

## Main Notebooks

- [Go_beyond/notebooks/network_structures_study.ipynb](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/notebooks/network_structures_study.ipynb)
- [Go_beyond/notebooks/d3_tetrahedra_study.ipynb](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/notebooks/d3_tetrahedra_study.ipynb)
- [Go_beyond/notebooks/heterogeneous_mu_study.ipynb](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/notebooks/heterogeneous_mu_study.ipynb)

## Running the Code

Local smoke verification:

```bash
python3 Go_beyond/verify_go_beyond.py
```

Notebook-driven experiments:

- open the notebooks in `Replication/notebooks/` or `Go_beyond/notebooks/`
- the go-beyond notebooks support `smoke_test` and `production` style settings

HPC production runs:

- large production scans were run on NYU Torch HPC
- GPU-based runners are saved in [Go_beyond/results](/Users/xialeihuang/Desktop/NYU%20Shanghai%20courses/Networks%20and%20Dynamics/Final_Project/simplagion-master/Go_beyond/results)
- the repository includes both the run scripts and the generated outputs used in the report

## Citation

Original paper:

I. Iacopini, G. Petri, A. Barrat, and V. Latora (2019), *Simplicial Models of Social Contagion*, Nature Communications 10(1), 2485.

## Notes

- The root-level notebooks are preserved from the original codebase for reference.
- The project report and final figures are based primarily on the contents of `Replication/` and `Go_beyond/`.
- Some large intermediate transfer archives are intentionally not part of the tracked project outputs.
