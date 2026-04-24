import numpy as np


def find_cut(rhos_array):
    non_zero = np.count_nonzero(rhos_array, axis=0) > 1
    return min(np.argwhere(non_zero))[0]


def parse_results(results, cut=False):
    rhos_array = []
    k1_list = []
    k2_list = []
    k3_list = []

    for result in results:
        rhos_array.append(result["rhos"])
        k1_list.append(result["avg_k1"])
        k2_list.append(result["avg_k2"])
        k3_list.append(result.get("avg_k3", 0.0))

    rhos_array = np.array(rhos_array, dtype=float)
    k1_list = np.array(k1_list, dtype=float)
    k2_list = np.array(k2_list, dtype=float)
    k3_list = np.array(k3_list, dtype=float)

    if cut:
        cut_point = find_cut(rhos_array)
        clean = []
        for rhos in rhos_array:
            current = []
            for i, rr in enumerate(rhos):
                if i < cut_point:
                    current.append(rr)
                elif rr == 0:
                    current.append(np.nan)
                else:
                    current.append(rr)
            clean.append(current)
        rhos_array = np.array(clean, dtype=float)

    avg_rhos = np.nan_to_num(np.nanmean(rhos_array, axis=0))
    std_rhos = np.nan_to_num(np.nanstd(rhos_array, axis=0))
    sem_rhos = np.nan_to_num(std_rhos / np.sqrt(max(len(results), 1)))

    return {
        "avg_rhos": avg_rhos,
        "std_rhos": std_rhos,
        "sem_rhos": sem_rhos,
        "avg_k1": float(k1_list.mean()) if len(k1_list) else 0.0,
        "avg_k2": float(k2_list.mean()) if len(k2_list) else 0.0,
        "avg_k3": float(k3_list.mean()) if len(k3_list) else 0.0,
        "n_sims": len(results),
    }

