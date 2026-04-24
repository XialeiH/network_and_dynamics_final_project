from pathlib import Path
import sys
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.go_beyond_experiments import run_prevalence_scan, save_pickle
from core.go_beyond_generators import generate_family_complex
from core.go_beyond_plotstyle import apply_style, ensure_output_dirs
from core.go_beyond_results import parse_results

apply_style()
FIGURES_DIR, RESULTS_DIR = ensure_output_dirs()

PROFILE = 'production'
N = 2000
MU = 0.05
T_MAX = 4000
N_SIMS = 80
LAMBDA1S = np.linspace(0.2, 2.2, 30)
LAMBDA2_TARGET = 0.8
SEED_PCT = 5

controlled_specs = {
    'er': {'k1': 16, 'k2': 4},
    'scale_free': {'k1': 16, 'k2': 4},
    'small_world': {'k1': 16, 'k2': 4},
}

native_specs = {
    'er': {'p1': 0.008, 'p2': 0.00001},
    'scale_free': {'m': 8, 'triangle_factor': 4.0},
    'small_world': {'k_nearest': 16, 'rewiring_prob': 0.12, 'triangle_factor': 4.0},
}

styles = {
    'er': dict(marker='o', color='black', mfc='white', label='ER / RSC'),
    'scale_free': dict(marker='s', color='darkorange', mfc='white', label='Scale-free'),
    'small_world': dict(marker='^', color='cornflowerblue', mfc='white', label='Small-world'),
}


def load_pickle(path: Path):
    with path.open('rb') as handle:
        return pickle.load(handle)

for mode_name, specs, fig_name, pkl_name, seed in [
    ('controlled', controlled_specs, f'network_structures_controlled_{PROFILE}.png', f'network_structures_controlled_{PROFILE}.pkl', 11),
    ('native', native_specs, f'network_structures_native_{PROFILE}.png', f'network_structures_native_{PROFILE}.pkl', 19),
]:
    payload = {}
    fig = plt.figure(figsize=(4.8, 3.4))
    ax = plt.subplot(111)
    for family, spec in specs.items():
        checkpoint_path = RESULTS_DIR / f'{mode_name}_{family}_{PROFILE}_checkpoint.pkl'
        if checkpoint_path.exists():
            print(f'[{mode_name}] loading existing checkpoint for {family}...', flush=True)
            payload[family] = load_pickle(checkpoint_path)
        else:
            print(f'[{mode_name}] building {family} network...', flush=True)
            complex_data = generate_family_complex(
                family=family,
                mode=mode_name,
                n_nodes=N,
                max_dimension=2,
                seed=seed,
                **spec,
            )
            print(f'[{mode_name}] running prevalence scan for {family}...', flush=True)
            results = run_prevalence_scan(
                complex_data,
                lambda1s=LAMBDA1S,
                lambda2_target=LAMBDA2_TARGET,
                seed_pct=SEED_PCT,
                t_max=T_MAX,
                mu=MU,
                n_sims=N_SIMS,
            )
            summary = parse_results(results, cut=False)
            payload[family] = {'complex_data': complex_data, 'results': results, 'summary': summary}
            save_pickle(checkpoint_path, payload[family])
            print(f'[{mode_name}] finished {family}', flush=True)

        summary = payload[family]['summary']
        sty = styles[family].copy()
        label = sty.pop('label')
        color = sty['color']
        mfc = sty.pop('mfc')
        ax.plot(LAMBDA1S, summary['avg_rhos'], '-', linewidth=1.2, ms=6, mfc=mfc, **sty, label=label)
        ax.errorbar(LAMBDA1S, summary['avg_rhos'], yerr=summary['sem_rhos'], fmt='none', color=color, alpha=0.45, capsize=2, elinewidth=0.8)
    ax.set_xlabel('Rescaled infectivity, lambda', size=12)
    ax.set_ylabel('Density of infected nodes, rho*', size=12)
    ax.set_xlim(0.2, 2.2)
    ax.set_ylim(-0.01, 0.85)
    ax.legend(fontsize=9, handlelength=1.1, handletextpad=0.4, borderaxespad=0.2, loc='upper left')
    ax.set_title('Controlled network comparison (production)' if mode_name == 'controlled' else 'Native-parameter comparison (production)', fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / fig_name, dpi=150, bbox_inches='tight')
    plt.close(fig)
    save_pickle(RESULTS_DIR / pkl_name, payload)
    print(f'[{mode_name}] saved aggregate outputs', flush=True)

print('Production network structure run completed.', flush=True)
