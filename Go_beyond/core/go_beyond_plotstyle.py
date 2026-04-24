from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
FIGURES_DIR = BASE_DIR / "figures"
RESULTS_DIR = BASE_DIR / "results"


def apply_style():
    plt.rcParams["xtick.major.width"] = 1.2
    plt.rcParams["ytick.major.width"] = 1.2
    plt.rcParams["axes.linewidth"] = 1.2
    plt.rcParams["figure.figsize"] = (4.5, 3.0)
    plt.rcParams["font.size"] = 11


def ensure_output_dirs():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR, RESULTS_DIR

