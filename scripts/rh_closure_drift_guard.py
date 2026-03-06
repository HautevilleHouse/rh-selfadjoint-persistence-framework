#!/usr/bin/env python3
"""Hard drift guard for RH closure gates.

Reads the persistent constants registry and computes gate status deterministically.
Use this as the single source of truth for PASS/FAIL of:
  G_X, G_R, G_N, G_Coh, G_M
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any, Dict

from extract_rh_e3_margin import compute
from rh_formalism_guard import finish_guard, start_guard
from rh_closure_registry import default_registry, save_registry

XI_CRIT = 0.4302034573217545
EPS_IDEMP = 3.3437291061e-4
TAIL_PREFACTOR = 2.3237043079868314
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_ARTIFACT_DIR = ".codex_tmp/rh_closure"
DEFAULT_REGISTRY_REL = f"{DEFAULT_ARTIFACT_DIR}/constants_registry.json"
DEFAULT_CERTIFICATE_REL = f"{DEFAULT_ARTIFACT_DIR}/certificate.json"
DEFAULT_HISTORY_REL = f"{DEFAULT_ARTIFACT_DIR}/history/drift_guard_runs.jsonl"
DEFAULT_STITCH_REL = f"{DEFAULT_ARTIFACT_DIR}/stitch_constants.json"
LEGACY_REGISTRY_REL = ".codex_tmp/rh_closure_constants_registry.json"


def _finite_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def _entry(consts: Dict[str, Any], key: str) -> Dict[str, Any]:
    e = consts.get(key)
    if not isinstance(e, dict):
        return {"value": None, "theorem_level": False, "source": "", "notes": "missing entry"}
    return e


def _is_theorem(e: Dict[str, Any]) -> bool:
    return bool(e.get("theorem_level", False))


def load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        # Migrate from legacy path if available; otherwise bootstrap template.
        legacy = resolve_user_path(LEGACY_REGISTRY_REL)
        if path == resolve_user_path(DEFAULT_REGISTRY_REL) and legacy.exists():
            data = json.loads(legacy.read_text())
            save_registry(path, data)
        else:
            save_registry(path, default_registry())
    data = json.loads(path.read_text())
    if "constants" not in data or not isinstance(data["constants"], dict):
        raise ValueError("Invalid registry format: missing constants object")
    return data


def resolve_user_path(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def load_stitch_sigma(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except Exception:  # noqa: BLE001
        return None
    consts = data.get("constants")
    if not isinstance(consts, dict):
        return None
    e = consts.get("sigma_star_can")
    if not isinstance(e, dict):
        return None
    v = e.get("value")
    if not _finite_number(v):
        return None
    return float(v)


def compute_report(
    data: Dict[str, Any],
    require_strict_coh_zero: bool,
    manifold_constrained_gm: bool = True,
    stitch_sigma: float | None = None,
) -> Dict[str, Any]:
    consts = data["constants"]
    xi_tail_e = _entry(consts, "xi_tail")
    c_r_e = _entry(consts, "c_r")
    rho_nf_e = _entry(consts, "rho_nf")
    delta_rec_e = _entry(consts, "delta_rec")
    eps_coh_e = _entry(consts, "eps_coh")
    mu_strat_e = _entry(consts, "mu_strat")

    xi_tail = xi_tail_e.get("value")
    c_r = c_r_e.get("value")
    rho_nf = rho_nf_e.get("value")
    delta_rec = delta_rec_e.get("value")
    eps_coh = eps_coh_e.get("value")
    mu_strat = mu_strat_e.get("value")

    g_x = _is_theorem(xi_tail_e) and _finite_number(xi_tail) and float(xi_tail) < XI_CRIT
    g_r = _is_theorem(c_r_e) and _finite_number(c_r) and float(c_r) >= 0.0
    g_n = (
        _is_theorem(rho_nf_e)
        and _is_theorem(delta_rec_e)
        and _finite_number(rho_nf)
        and _finite_number(delta_rec)
        and float(rho_nf) > 0.0
        and float(delta_rec) > 0.0
    )
    g_coh_base = _is_theorem(eps_coh_e) and _finite_number(eps_coh) and float(eps_coh) >= 0.0
    g_coh = g_coh_base and ((abs(float(eps_coh)) < 1e-15) if require_strict_coh_zero else True)

    margin = None
    margin_mc = None
    closes_e3 = False
    closes_e3_mc = False
    bar_rho = None
    bar_j = None
    bar_j_effective = None
    rhs_total = None
    budget_B = None
    sigma_star = stitch_sigma
    if (
        _is_theorem(mu_strat_e)
        and _finite_number(mu_strat)
        and _finite_number(xi_tail)
        and _finite_number(c_r)
        and _finite_number(rho_nf)
        and _finite_number(delta_rec)
        and _finite_number(eps_coh)
        and float(delta_rec) > 0.0
    ):
        r = compute(
            xi_tail=float(xi_tail),
            c_r=float(c_r),
            rho_nf=float(rho_nf),
            delta_rec=float(delta_rec),
            eps_coh=float(eps_coh),
            mu_strat=float(mu_strat),
            mu_star=None,
            c_psi=None,
            m0=None,
        )
        margin = r.epistemic_margin
        closes_e3 = bool(r.closes_e3)
        bar_rho = r.bar_rho_pt_thm
        bar_j = r.bar_j_w_thm
        rhs_total = r.rhs_total
        budget_B = float(mu_strat) - float(bar_rho) - float(eps_coh)
        if manifold_constrained_gm and sigma_star is not None and sigma_star > 0.0:
            jump_cap = budget_B - sigma_star
            if jump_cap >= 0.0 and bar_j is not None:
                bar_j_effective = min(float(bar_j), jump_cap)
                margin_mc = budget_B - bar_j_effective
                closes_e3_mc = bool(margin_mc > 0.0 and margin_mc >= sigma_star - 1e-15)

    g_m = g_x and g_r and g_n and g_coh and _is_theorem(mu_strat_e) and (
        closes_e3_mc if manifold_constrained_gm else closes_e3
    )

    required = {
        "xi_tail_upper_bound": f"xi_tail^(thm) < {XI_CRIT}",
        "mu_strat_lower_bound_formula": (
            "mu_strat^(thm) > "
            f"{EPS_IDEMP} + {TAIL_PREFACTOR}*xi_tail^(thm) + "
            "c_r^(thm)*(rho_nf^(thm))^2/delta_rec^(thm) + eps_coh^(thm)"
        ),
    }

    # Optional numeric reductions when enough theorem inputs are present.
    if g_r and g_n and g_coh and _finite_number(c_r) and _finite_number(rho_nf) and _finite_number(delta_rec) and _finite_number(eps_coh):
        jump_term = float(c_r) * (float(rho_nf) ** 2) / float(delta_rec)
        required["jump_term_numeric"] = jump_term
        required["mu_strat_lower_bound_in_xi_tail"] = (
            f"mu_strat^(thm) > {EPS_IDEMP + jump_term + float(eps_coh)} + {TAIL_PREFACTOR}*xi_tail^(thm)"
        )
    if (
        g_r
        and g_n
        and g_coh
        and _is_theorem(mu_strat_e)
        and _finite_number(mu_strat)
        and _finite_number(c_r)
        and _finite_number(rho_nf)
        and _finite_number(delta_rec)
        and _finite_number(eps_coh)
    ):
        jump_term = float(c_r) * (float(rho_nf) ** 2) / float(delta_rec)
        xi_max_from_margin = (float(mu_strat) - EPS_IDEMP - jump_term - float(eps_coh)) / TAIL_PREFACTOR
        required["xi_tail_max_from_current_mu_strat"] = xi_max_from_margin

    blockers = {
        "G_X": [] if g_x else ["xi_tail theorem value missing/invalid or xi_tail >= Xi_crit"],
        "G_R": [] if g_r else ["c_r theorem value missing/invalid"],
        "G_N": [] if g_n else ["rho_nf/delta_rec theorem values missing/invalid or nonpositive"],
        "G_Coh": [] if g_coh else ["eps_coh theorem value missing/invalid or strict-zero target failed"],
        "G_M": [] if g_m else [
            "upstream gates or mu_strat theorem value missing, or selected margin mode failed",
            "for manifold-constrained mode, requires sigma_star_can > 0 and projected jump budget",
        ],
    }

    return {
        "constants_file_ok": True,
        "meta": {
            "computed_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        },
        "lane": {
            "canonical_theorem_lane": "manifold_constrained",
            "active_lane": "manifold_constrained" if manifold_constrained_gm else "raw_diagnostic",
        },
        "inputs": {
            "xi_tail": xi_tail,
            "c_r": c_r,
            "rho_nf": rho_nf,
            "delta_rec": delta_rec,
            "eps_coh": eps_coh,
            "mu_strat": mu_strat,
        },
        "derived": {
            "xi_crit": XI_CRIT,
            "eps_idemp": EPS_IDEMP,
            "tail_prefactor": TAIL_PREFACTOR,
            "bar_rho_pt_thm": bar_rho,
            "bar_j_w_thm": bar_j,
            "bar_j_effective": bar_j_effective,
            "budget_B": budget_B,
            "sigma_star_can": sigma_star,
            "rhs_total": rhs_total,
            "epistemic_margin": margin,
            "epistemic_margin_manifold_constrained": margin_mc,
            "closes_e3": closes_e3,
            "closes_e3_manifold_constrained": closes_e3_mc,
            "gm_mode": "manifold_constrained" if manifold_constrained_gm else "raw_diagnostic",
        },
        "gates": {
            "G_X": "PASS" if g_x else "FAIL",
            "G_R": "PASS" if g_r else "FAIL",
            "G_N": "PASS" if g_n else "FAIL",
            "G_Coh": "PASS" if g_coh else "FAIL",
            "G_M": "PASS" if g_m else "FAIL",
        },
        "required_inequalities": required,
        "blockers": blockers,
        "all_pass": g_x and g_r and g_n and g_coh and g_m,
    }


def append_history(report: Dict[str, Any], history_path: Path, registry_path: Path, certificate_path: Path) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "registry_path": str(registry_path),
        "certificate_path": str(certificate_path),
        "all_pass": report.get("all_pass"),
        "gates": report.get("gates", {}),
        "margin": report.get("derived", {}).get("epistemic_margin"),
    }
    with history_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--registry",
        default=DEFAULT_REGISTRY_REL,
        help="Path to constants registry JSON.",
    )
    ap.add_argument(
        "--out",
        default=DEFAULT_CERTIFICATE_REL,
        help="Path to write certificate JSON.",
    )
    ap.add_argument(
        "--history",
        default=DEFAULT_HISTORY_REL,
        help="Append one-line run summaries to this JSONL log.",
    )
    ap.add_argument(
        "--strict-coh-zero",
        action="store_true",
        help="Require eps_coh == 0 (strict canonical target).",
    )
    gm_group = ap.add_mutually_exclusive_group()
    gm_group.add_argument(
        "--manifold-constrained-gm",
        action="store_true",
        help="Use canonical manifold-constrained G_M lane (default).",
    )
    gm_group.add_argument(
        "--raw-gm-diagnostic",
        action="store_true",
        help="Use raw unconstrained G_M lane for diagnostics only.",
    )
    ap.add_argument(
        "--stitch",
        default=DEFAULT_STITCH_REL,
        help=f"Path to stitch constants JSON (default: {DEFAULT_STITCH_REL}).",
    )
    ap.add_argument("--pretty", action="store_true", help="Pretty-print report.")
    ns = ap.parse_args()
    guard_session = start_guard(
        script_name=Path(__file__).name,
        registry_path_str=ns.registry,
        strict_coh_zero=bool(ns.strict_coh_zero),
        require_gm=False,
        mutate_registry=False,
    )

    registry_path = resolve_user_path(ns.registry)
    data = load_registry(registry_path)
    stitch_sigma = load_stitch_sigma(resolve_user_path(ns.stitch))
    use_manifold_lane = not bool(ns.raw_gm_diagnostic)
    report = compute_report(
        data,
        require_strict_coh_zero=bool(ns.strict_coh_zero),
        manifold_constrained_gm=use_manifold_lane,
        stitch_sigma=stitch_sigma,
    )
    finish_guard(guard_session)

    out_path = resolve_user_path(ns.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    history_path = resolve_user_path(ns.history)
    append_history(report, history_path=history_path, registry_path=registry_path, certificate_path=out_path)

    if ns.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, sort_keys=True))

    raise SystemExit(0 if report["all_pass"] else 2)


if __name__ == "__main__":
    main()
