from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass(frozen=True)
class FixedPoint:
    rho: float
    stable: bool
    kind: str


def mean_field_rhs(rho, lambda1, lambda2=0.0, lambda3=0.0, mu=1.0):
    """Mean-field RHS for the D=3 simplicial contagion model.

    In rescaled time tau = mu * t and with
      lambda1 = beta1 <k1> / mu
      lambda2 = beta2 <k2> / mu
      lambda3 = beta3 <k3> / mu

    the homogeneous-mixing equation is

      d rho / d tau = -rho + (1-rho) * (lambda1 rho + lambda2 rho^2 + lambda3 rho^3)

    which reduces to the D=2 form in the paper when lambda3 = 0.
    """

    rho = np.asarray(rho, dtype=float)
    return mu * (-rho + (1.0 - rho) * (lambda1 * rho + lambda2 * rho**2 + lambda3 * rho**3))


def endemic_cubic_coefficients(lambda1, lambda2=0.0, lambda3=0.0):
    """Cubic coefficients for non-zero fixed points.

    Positive stationary states rho > 0 solve

      lambda3 rho^3 + (lambda2 - lambda3) rho^2 + (lambda1 - lambda2) rho + (1 - lambda1) = 0
    """

    return np.array([lambda3, lambda2 - lambda3, lambda1 - lambda2, 1.0 - lambda1], dtype=float)


def _poly_derivative(rho, lambda1, lambda2=0.0, lambda3=0.0):
    return (lambda1 - 1.0) + 2.0 * (lambda2 - lambda1) * rho + 3.0 * (lambda3 - lambda2) * rho**2 - 4.0 * lambda3 * rho**3


def classify_fixed_points(lambda1, lambda2=0.0, lambda3=0.0, tol=1e-9):
    fixed_points: List[FixedPoint] = []
    zero_stable = lambda1 < 1.0
    fixed_points.append(FixedPoint(rho=0.0, stable=zero_stable, kind="disease_free"))

    coeffs = endemic_cubic_coefficients(lambda1, lambda2, lambda3)
    roots = np.roots(coeffs)
    real_roots = sorted(
        float(np.real(root))
        for root in roots
        if abs(np.imag(root)) < 1e-8 and tol < np.real(root) < 1.0 - tol
    )

    deduped = []
    for root in real_roots:
        if not deduped or abs(root - deduped[-1]) > 1e-6:
            deduped.append(root)

    for root in deduped:
        fixed_points.append(
            FixedPoint(rho=root, stable=_poly_derivative(root, lambda1, lambda2, lambda3) < 0.0, kind="endemic")
        )
    return fixed_points


def has_healthy_endemic_bistability(lambda1, lambda2=0.0, lambda3=0.0, tol=1e-9):
    fixed_points = classify_fixed_points(lambda1, lambda2, lambda3, tol=tol)
    disease_free = fixed_points[0]
    positive_stable = [fp for fp in fixed_points[1:] if fp.stable]
    positive_unstable = [fp for fp in fixed_points[1:] if not fp.stable]
    return disease_free.stable and bool(positive_stable) and bool(positive_unstable)


def fold_surface_from_rho_lambda3(rho, lambda3):
    """Saddle-node surface parameterized by rho in (0, 1) and lambda3.

    Solving the fold conditions F(rho)=0 and dF/drho=0 gives:

      lambda2 = 1 / (1-rho)^2 - 2 lambda3 rho
      lambda1 = (1 - 2 rho) / (1-rho)^2 + lambda3 rho^2

    For lambda3 = 0 this reduces to the D=2 fold curve of the paper.
    """

    rho = np.asarray(rho, dtype=float)
    one_minus = 1.0 - rho
    lambda2 = 1.0 / one_minus**2 - 2.0 * lambda3 * rho
    lambda1 = (1.0 - 2.0 * rho) / one_minus**2 + lambda3 * rho**2
    return lambda1, lambda2


def fold_surface_from_rho_lambda2(rho, lambda2):
    rho = np.asarray(rho, dtype=float)
    one_minus = 1.0 - rho
    lambda3 = (1.0 / one_minus**2 - lambda2) / (2.0 * rho)
    lambda1 = (1.0 - 2.0 * rho) / one_minus**2 + lambda3 * rho**2
    return lambda1, lambda3


def cusp_lambda2_from_lambda3(lambda3):
    """Onset curve of healthy-endemic bistability on the lambda1 = 1 plane.

    Physical rho in [0, 1) implies lambda3 >= 1. Along the cusp:

      lambda2 = 2 sqrt(lambda3) - lambda3

    which generalizes the D=2 condition lambda1^c = 2 sqrt(lambda2) - lambda2.
    """

    lambda3 = np.asarray(lambda3, dtype=float)
    out = np.full_like(lambda3, np.nan, dtype=float)
    mask = (lambda3 >= 1.0) & (lambda3 <= 4.0)
    out[mask] = 2.0 * np.sqrt(lambda3[mask]) - lambda3[mask]
    return out


def unstable_positive_fixed_points(lambda1, lambda2=0.0, lambda3=0.0, tol=1e-9):
    return [
        fp
        for fp in classify_fixed_points(lambda1, lambda2, lambda3, tol=tol)
        if fp.kind == "endemic" and not fp.stable
    ]


def stable_positive_fixed_points(lambda1, lambda2=0.0, lambda3=0.0, tol=1e-9):
    return [
        fp
        for fp in classify_fixed_points(lambda1, lambda2, lambda3, tol=tol)
        if fp.kind == "endemic" and fp.stable
    ]


def select_representative_bistable_lambda1(
    lambda2,
    lambda3,
    lambda1_min=0.2,
    lambda1_max=2.2,
    n_points=4001,
):
    lambda1_grid = np.linspace(lambda1_min, lambda1_max, n_points)
    bistable = [float(val) for val in lambda1_grid if has_healthy_endemic_bistability(val, lambda2, lambda3)]
    if not bistable:
        raise ValueError(
            f"No healthy-endemic bistable lambda1 found for lambda2={lambda2}, lambda3={lambda3} "
            f"inside [{lambda1_min}, {lambda1_max}]"
        )

    chosen = float(bistable[len(bistable) // 2])
    fixed_points = classify_fixed_points(chosen, lambda2, lambda3)
    unstable = unstable_positive_fixed_points(chosen, lambda2, lambda3)
    stable = stable_positive_fixed_points(chosen, lambda2, lambda3)
    return {
        "lambda1": chosen,
        "window": [float(bistable[0]), float(bistable[-1])],
        "fixed_points": fixed_points,
        "unstable_root": float(unstable[0].rho) if unstable else None,
        "stable_endemic_root": float(stable[-1].rho) if stable else None,
    }
