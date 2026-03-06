#!/usr/bin/env python3
"""Compute E3/epistemic margin quantities for RH closure.

This script instantiates the quantities introduced in Section 13.53M/13.53O:
  - bar rho_(PT,*)^(thm)
  - bar j_(W,*)^(thm)
  - eps_(coh,*)
  - epistemic closure margin mathfrak M_(RH,epi,*)

Known theorem-level numeric constants from the manuscript:
  eps_idemp = 3.3437291061e-4
  tail_prefactor = 2.3237043079868314
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from rh_formalism_guard import finish_guard, start_guard


EPS_IDEMP = 3.3437291061e-4
TAIL_PREFACTOR = 2.3237043079868314


@dataclass
class MarginResult:
    xi_tail: float
    c_r: float
    rho_nf: float
    delta_rec: float
    eps_coh: float
    bar_rho_pt_thm: float
    bar_j_w_thm: float
    rhs_total: float
    mu_strat: Optional[float]
    epistemic_margin: Optional[float]
    closes_e3: Optional[bool]
    xi_tail_max_if_mu_strat_given: Optional[float]
    jump_rate_max_if_mu_strat_given: Optional[float]
    jump_rate_dg3_upper_bound: Optional[float]


def compute(
    xi_tail: float,
    c_r: float,
    rho_nf: float,
    delta_rec: float,
    eps_coh: float,
    mu_strat: Optional[float],
    mu_star: Optional[float],
    c_psi: Optional[float],
    m0: Optional[float],
) -> MarginResult:
    if delta_rec <= 0:
        raise ValueError("delta_rec must be > 0")
    if rho_nf < 0:
        raise ValueError("rho_nf must be >= 0")
    if eps_coh < 0:
        raise ValueError("eps_coh must be >= 0")

    bar_rho = EPS_IDEMP + TAIL_PREFACTOR * xi_tail
    bar_j = c_r * (rho_nf**2) / delta_rec
    rhs = bar_rho + bar_j + eps_coh

    margin = None
    closes = None
    xi_tail_max = None
    jump_rate_max = None

    if mu_strat is not None:
        margin = mu_strat - rhs
        closes = margin > 0.0
        # Solve mu_strat > eps_idemp + tail_pref*xi_tail + bar_j + eps_coh
        xi_tail_max = (mu_strat - EPS_IDEMP - bar_j - eps_coh) / TAIL_PREFACTOR
        # Solve for admissible jump-rate term:
        jump_rate_max = mu_strat - EPS_IDEMP - TAIL_PREFACTOR * xi_tail - eps_coh

    jump_rate_dg3_bound = None
    if mu_star is not None and c_psi is not None and m0 is not None:
        jump_rate_dg3_bound = mu_star * c_psi * (m0**2)

    return MarginResult(
        xi_tail=xi_tail,
        c_r=c_r,
        rho_nf=rho_nf,
        delta_rec=delta_rec,
        eps_coh=eps_coh,
        bar_rho_pt_thm=bar_rho,
        bar_j_w_thm=bar_j,
        rhs_total=rhs,
        mu_strat=mu_strat,
        epistemic_margin=margin,
        closes_e3=closes,
        xi_tail_max_if_mu_strat_given=xi_tail_max,
        jump_rate_max_if_mu_strat_given=jump_rate_max,
        jump_rate_dg3_upper_bound=jump_rate_dg3_bound,
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xi-tail", type=float, required=True, help="Xi_(tail,*) value")
    p.add_argument("--c-r", type=float, required=True, help="C_(R,*) value")
    p.add_argument("--rho-nf", type=float, required=True, help="rho_(nf) value")
    p.add_argument("--delta-rec", type=float, required=True, help="delta_(rec) value")
    p.add_argument(
        "--eps-coh",
        type=float,
        default=0.0,
        help="eps_(coh,*) value (default: 0 for strict coherence)",
    )
    p.add_argument(
        "--mu-strat",
        type=float,
        default=None,
        help="mu_(strat,*) value (optional; enables closure test)",
    )
    p.add_argument(
        "--mu-star",
        type=float,
        default=None,
        help="mu_* value for DG3-derived jump-rate bound (optional)",
    )
    p.add_argument(
        "--c-psi",
        type=float,
        default=None,
        help="c_(Psi,*) value for DG3-derived jump-rate bound (optional)",
    )
    p.add_argument(
        "--m0",
        type=float,
        default=None,
        help="m_0 value for DG3-derived jump-rate bound (optional)",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    return p.parse_args()


def main() -> None:
    ns = parse_args()
    guard_session = start_guard(
        script_name=Path(__file__).name,
        registry_path_str=None,
        strict_coh_zero=True,
        require_gm=False,
        mutate_registry=False,
    )
    result = compute(
        xi_tail=ns.xi_tail,
        c_r=ns.c_r,
        rho_nf=ns.rho_nf,
        delta_rec=ns.delta_rec,
        eps_coh=ns.eps_coh,
        mu_strat=ns.mu_strat,
        mu_star=ns.mu_star,
        c_psi=ns.c_psi,
        m0=ns.m0,
    )
    finish_guard(guard_session)
    if ns.pretty:
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
    else:
        print(json.dumps(asdict(result), sort_keys=True))


if __name__ == "__main__":
    main()
