"""
fig2_full_v2.py
──────────────────────────────────────────────────────────────────────
Reproduces Fig 2 of Iacopini et al. (2019) for ONE dataset.
Only the prevalence curves (right panel), no network visualisation.

Reuses:
  - utils_simplagion_MC.py  → import_sociopattern_simcomp_SCM()
  - utils_simplagion_on_RSC.py → SimplagionModel, parse_results

Change DATASET to run other datasets:
    'InVS15' | 'SFHH' | 'LH10' | 'Thiers13'
──────────────────────────────────────────────────────────────────────
"""

import pickle, os
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool

from utils_simplagion_MC import import_sociopattern_simcomp_SCM
from utils_simplagion_on_RSC import SimplagionModel, parse_results

# ── Settings ──────────────────────────────────────────────────────────────────
DATASET      = 'Thiers13'
DATASET_DIR  = 'Data/Sociopatterns/thr_data_random/'
N_MINUTES    = 5
THR          = 0.80
MU           = 0.05
LAMBDA1S     = np.linspace(0, 2.0, 25)
LAMBDAD_LIST = [0.0, 0.8, 2.0, 2.0]
SEED_LIST    = [1,   1,   1,   40 ]
T_MAX        = 3000
N_SIMS       = 75
N_PROC       = 4
OUT_DIR      = 'Results_fig2/'

os.makedirs(OUT_DIR, exist_ok=True)


# ── Worker for parallel pool ────────────────────────────────────────────────
def run_one_sim(args):
    it, node_neighbors, triangles_list, lambda1s, lD_target, seed_pct, t_max, mu = args
    N      = len(node_neighbors)
    avg_k  = sum(len(v) for v in node_neighbors.values()) / N
    avg_kD = 3.0 * len(triangles_list) / N

    beta1s = mu / avg_k * lambda1s
    beta2  = mu / avg_kD * lD_target if avg_kD > 0 else 0.0

    model = SimplagionModel(node_neighbors, triangles_list, seed_pct)
    rhos = []
    for b1 in beta1s:
        model.reset() if hasattr(model, 'reset') else model.initial_setup(
            fixed_nodes_to_infect=model.initial_infected_nodes)
        model.run(t_max, b1, beta2, mu, print_status=False)
        rhos.append(model.get_stationary_rho(normed=True, last_k_values=100))

    print(f'  worker {it} done')
    return rhos, avg_k, avg_kD


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':

    # Load network
    node_neighbors, triangles_list, avg_k, avg_kD = import_sociopattern_simcomp_SCM(
        DATASET_DIR, DATASET, N_MINUTES, THR)
    print(f'Loaded {DATASET}: N={len(node_neighbors)}, '
          f'<k>={avg_k:.1f}, <kD>={avg_kD:.1f}')

    # Run simulations
    all_results = {}
    for lD, seed in zip(LAMBDAD_LIST, SEED_LIST):
        key = (lD, seed)
        print(f'\nRunning λ_Δ={lD}, seed={seed}%  ({N_SIMS} sims)...')
        args = [(i, node_neighbors, triangles_list,
                 LAMBDA1S, lD, seed, T_MAX, MU)
                for i in range(N_SIMS)]
        with Pool(processes=N_PROC) as pool:
            results = pool.map(run_one_sim, args)
        all_results[key] = results
        fname = OUT_DIR + f'result_{DATASET}_lD{lD}_seed{seed}.p'
        pickle.dump(results, open(fname, 'wb'))
        print(f'  Saved → {fname}')

    # ==================================================================
    # Plot: only prevalence curves (no network visualisation)
    # ==================================================================
    fig, ax = plt.subplots(1, 1, figsize=(6, 5))

    styles = {
        (0.0, 1):  dict(marker='o', color='cornflowerblue', mfc='white',
                        label=r'$\lambda_\Delta=0.0$'),
        (0.8, 1):  dict(marker='^', color='gray',           mfc='white',
                        label=r'$\lambda_\Delta=0.8$'),
        (2.0, 1):  dict(marker='s', color='darkorange',     mfc='white',
                        label=r'$\lambda_\Delta=2.0$'),
        (2.0, 40): dict(marker='s', color='darkorange',     mfc='white',
                        label=r'$\lambda_\Delta=2.0$'),
    }

    for lD, seed in zip(LAMBDAD_LIST, SEED_LIST):
        key = (lD, seed)
        use_cut = (lD >= 2.0 and seed == 1)
        avg_rhos, std_rhos, _, _ = parse_results(all_results[key], cut=use_cut, return_std=True)

        sty = styles[key].copy()
        label = sty.pop('label')
        mfc = sty.pop('mfc')
        color = sty['color']

        # 画数据点 + 实线连接
        ax.plot(LAMBDA1S, avg_rhos,
                linestyle='-', linewidth=1.2,
                mfc=mfc, ms=6, **sty, label=label)

        # 画误差线（标准误 sem）
        n_sims = len(all_results[key])
        sem_rhos = std_rhos / np.sqrt(n_sims)
        ax.errorbar(LAMBDA1S, avg_rhos, yerr=sem_rhos,
                    fmt='none', color=color, capsize=2, alpha=0.5, elinewidth=0.8)

    ax.set_xlabel(r'Rescaled infectivity $\lambda = \beta\langle k\rangle/\mu$',
                  fontsize=12)
    ax.set_ylabel(r'Density of infected nodes $\rho^*$', fontsize=12)
    ax.set_xlim(0, 2.0)
    ax.set_ylim(-0.02, 0.85)
    ax.legend(fontsize=10, loc='upper left')
    ax.set_title(f'Prevalence curves — {DATASET}', fontsize=11)

    plt.tight_layout()
    out_fig = OUT_DIR + f'fig2_{DATASET}.png'
    plt.savefig(out_fig, dpi=150, bbox_inches='tight')
    print(f'\nFigure saved → {out_fig}')
    plt.show()