#!/usr/bin/env python3
"""Compute quantitative target thresholds needed for G_M closure.

Reads theorem-tagged RH closure constants from the canonical registry and
computes the exact budget inequalities and one-parameter target thresholds:
  - max admissible jump term
  - c_r max (rho,delta fixed)
  - rho_nf max (c_r,delta fixed)
  - delta_rec min (c_r,rho fixed)
  - mu_strat min (others fixed)
  - xi_tail max (current jump fixed)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any, Dict

from rh_formalism_guard import finish_guard, start_guard

EPS_IDEMP = 3.3437291061e-4
TAIL_PREFACTOR = 2.3237043079868314
DEFAULT_REGISTRY = ".codex_tmp/rh_closure/constants_registry.json"
DEFAULT_OUT = ".codex_tmp/rh_closure/targets.json"
DEFAULT_OUT_MD = ".codex_tmp/rh_closure/targets.md"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def resolve_user_path(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def _load_registry(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text())
    if "constants" not in data or not isinstance(data["constants"], dict):
        raise ValueError("Invalid registry: missing constants object")
    return data["constants"]


def _val(constants: Dict[str, Any], key: str) -> float:
    e = constants.get(key)
    if not isinstance(e, dict):
        raise ValueError(f"Missing constant entry: {key}")
    v = e.get("value")
    if not isinstance(v, (int, float)) or not math.isfinite(float(v)):
        raise ValueError(f"Invalid numeric value for {key}: {v}")
    return float(v)


def compute_targets(constants: Dict[str, Any]) -> Dict[str, Any]:
    xi_tail = _val(constants, "xi_tail")
    c_r = _val(constants, "c_r")
    rho_nf = _val(constants, "rho_nf")
    delta_rec = _val(constants, "delta_rec")
    eps_coh = _val(constants, "eps_coh")
    mu_strat = _val(constants, "mu_strat")
    if delta_rec <= 0:
        raise ValueError("delta_rec must be > 0")
    if rho_nf <= 0:
        raise ValueError("rho_nf must be > 0")

    bar_rho = EPS_IDEMP + TAIL_PREFACTOR * xi_tail
    jump = c_r * (rho_nf**2) / delta_rec
    rhs = bar_rho + jump + eps_coh
    margin = mu_strat - rhs

    jump_budget_max = mu_strat - eps_coh - bar_rho
    ratio = (jump / jump_budget_max) if jump_budget_max > 0 else math.inf

    c_r_max = (jump_budget_max * delta_rec / (rho_nf**2)) if jump_budget_max > 0 else -math.inf
    rho_nf_max = math.sqrt(jump_budget_max * delta_rec / c_r) if jump_budget_max > 0 and c_r > 0 else -math.inf
    delta_rec_min = (c_r * (rho_nf**2) / jump_budget_max) if jump_budget_max > 0 else math.inf
    mu_strat_min = rhs
    xi_tail_max_with_current_jump = (mu_strat - eps_coh - EPS_IDEMP - jump) / TAIL_PREFACTOR

    return {
        "computed_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "inputs": {
            "xi_tail": xi_tail,
            "c_r": c_r,
            "rho_nf": rho_nf,
            "delta_rec": delta_rec,
            "eps_coh": eps_coh,
            "mu_strat": mu_strat,
        },
        "derived": {
            "eps_idemp": EPS_IDEMP,
            "tail_prefactor": TAIL_PREFACTOR,
            "bar_rho": bar_rho,
            "jump": jump,
            "rhs_total": rhs,
            "margin": margin,
            "jump_budget_max": jump_budget_max,
            "jump_over_budget_ratio": ratio,
        },
        "targets": {
            "c_r_max_if_rho_delta_fixed": c_r_max,
            "rho_nf_max_if_c_r_delta_fixed": rho_nf_max,
            "delta_rec_min_if_c_r_rho_fixed": delta_rec_min,
            "mu_strat_min_for_positive_margin": mu_strat_min,
            "xi_tail_max_with_current_jump": xi_tail_max_with_current_jump,
        },
        "multiplicative_adjustments": {
            "c_r_reduction_factor_needed": (c_r / c_r_max) if c_r_max > 0 else math.inf,
            "rho_nf_reduction_factor_needed": (rho_nf / rho_nf_max) if rho_nf_max > 0 else math.inf,
            "delta_rec_increase_factor_needed": (delta_rec_min / delta_rec) if delta_rec > 0 else math.inf,
            "mu_strat_increase_factor_needed": (mu_strat_min / mu_strat) if mu_strat > 0 else math.inf,
        },
        "closure_condition": (
            "mu_strat > eps_idemp + tail_prefactor*xi_tail + c_r*(rho_nf^2)/delta_rec + eps_coh"
        ),
    }


def render_md(report: Dict[str, Any]) -> str:
    i = report["inputs"]
    d = report["derived"]
    t = report["targets"]
    a = report["multiplicative_adjustments"]
    lines = [
        "# RH Closure Target Report",
        "",
        f"- computed_at_utc: `{report['computed_at_utc']}`",
        "",
        "## Inputs",
        f"- `xi_tail`: `{i['xi_tail']}`",
        f"- `c_r`: `{i['c_r']}`",
        f"- `rho_nf`: `{i['rho_nf']}`",
        f"- `delta_rec`: `{i['delta_rec']}`",
        f"- `eps_coh`: `{i['eps_coh']}`",
        f"- `mu_strat`: `{i['mu_strat']}`",
        "",
        "## Core Derived",
        f"- `bar_rho`: `{d['bar_rho']}`",
        f"- `jump`: `{d['jump']}`",
        f"- `rhs_total`: `{d['rhs_total']}`",
        f"- `margin`: `{d['margin']}`",
        f"- `jump_budget_max`: `{d['jump_budget_max']}`",
        f"- `jump_over_budget_ratio`: `{d['jump_over_budget_ratio']}`",
        "",
        "## One-Parameter Targets",
        f"- `c_r_max_if_rho_delta_fixed`: `{t['c_r_max_if_rho_delta_fixed']}`",
        f"- `rho_nf_max_if_c_r_delta_fixed`: `{t['rho_nf_max_if_c_r_delta_fixed']}`",
        f"- `delta_rec_min_if_c_r_rho_fixed`: `{t['delta_rec_min_if_c_r_rho_fixed']}`",
        f"- `mu_strat_min_for_positive_margin`: `{t['mu_strat_min_for_positive_margin']}`",
        f"- `xi_tail_max_with_current_jump`: `{t['xi_tail_max_with_current_jump']}`",
        "",
        "## Required Adjustment Factors",
        f"- `c_r_reduction_factor_needed`: `{a['c_r_reduction_factor_needed']}`",
        f"- `rho_nf_reduction_factor_needed`: `{a['rho_nf_reduction_factor_needed']}`",
        f"- `delta_rec_increase_factor_needed`: `{a['delta_rec_increase_factor_needed']}`",
        f"- `mu_strat_increase_factor_needed`: `{a['mu_strat_increase_factor_needed']}`",
        "",
        "## Closure Condition",
        f"- `{report['closure_condition']}`",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", default=DEFAULT_REGISTRY, help=f"Registry JSON path (default: {DEFAULT_REGISTRY})")
    p.add_argument("--out", default=DEFAULT_OUT, help=f"Output JSON report path (default: {DEFAULT_OUT})")
    p.add_argument("--out-md", default=DEFAULT_OUT_MD, help=f"Output Markdown report path (default: {DEFAULT_OUT_MD})")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON report.")
    return p


def main() -> None:
    ns = build_parser().parse_args()
    guard_session = start_guard(
        script_name=Path(__file__).name,
        registry_path_str=ns.registry,
        strict_coh_zero=True,
        require_gm=False,
        mutate_registry=False,
    )
    reg_path = resolve_user_path(ns.registry)
    constants = _load_registry(reg_path)
    report = compute_targets(constants)
    finish_guard(guard_session)

    out_path = resolve_user_path(ns.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    out_md = resolve_user_path(ns.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_md(report))

    if ns.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
