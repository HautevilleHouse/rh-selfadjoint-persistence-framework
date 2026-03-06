#!/usr/bin/env python3
"""Hard formalism guard for RH compute scripts.

This module enforces two layers before any RH compute script emits outputs:

1) Object-level manifold invariants on the canonical registry.
2) Higher-order functor/coherence invariants on stitch constants.

Pre-check and post-check must both pass. For registry-mutating scripts,
post-check failure restores the registry snapshot automatically.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

XI_CRIT = 0.4302034573217545
EPS_IDEMP = 3.3437291061e-4
TAIL_PREFACTOR = 2.3237043079868314

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_REGISTRY_REL = ".codex_tmp/rh_closure/constants_registry.json"
DEFAULT_STITCH_REL = ".codex_tmp/rh_closure/stitch_constants.json"

REQUIRED_REGISTRY_KEYS = (
    "xi_tail",
    "c_r",
    "rho_nf",
    "delta_rec",
    "eps_coh",
    "mu_strat",
)


@dataclass
class GuardSession:
    script_name: str
    registry_path: Path
    stitch_path: Path
    strict_coh_zero: bool
    require_gm: bool
    mutate_registry: bool
    registry_snapshot: Optional[str]


def resolve_user_path(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def _entry(consts: Dict[str, Any], key: str) -> Dict[str, Any]:
    e = consts.get(key)
    if not isinstance(e, dict):
        return {"value": None, "theorem_level": False, "source": "", "notes": "missing"}
    return e


def _is_theorem(entry: Dict[str, Any]) -> bool:
    return bool(entry.get("theorem_level", False))


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Invalid JSON object at {path}")
    return data


def _evaluate_registry(data: Dict[str, Any], strict_coh_zero: bool) -> Dict[str, Any]:
    consts = data.get("constants")
    if not isinstance(consts, dict):
        return {
            "pass": False,
            "reason": "registry missing constants object",
            "gates": {"G_X": False, "G_R": False, "G_N": False, "G_Coh": False, "G_M": False},
            "derived": {},
            "inputs": {},
        }

    missing_keys = [k for k in REQUIRED_REGISTRY_KEYS if k not in consts or not isinstance(consts.get(k), dict)]

    xi_e = _entry(consts, "xi_tail")
    c_e = _entry(consts, "c_r")
    rho_e = _entry(consts, "rho_nf")
    delta_e = _entry(consts, "delta_rec")
    eps_e = _entry(consts, "eps_coh")
    mu_e = _entry(consts, "mu_strat")

    xi = xi_e.get("value")
    c_r = c_e.get("value")
    rho = rho_e.get("value")
    delta = delta_e.get("value")
    eps = eps_e.get("value")
    mu = mu_e.get("value")

    g_x = _is_theorem(xi_e) and _finite(xi) and float(xi) < XI_CRIT
    g_r = _is_theorem(c_e) and _finite(c_r) and float(c_r) >= 0.0
    g_n = (
        _is_theorem(rho_e)
        and _is_theorem(delta_e)
        and _finite(rho)
        and _finite(delta)
        and float(rho) > 0.0
        and float(delta) > 0.0
    )
    g_coh_base = _is_theorem(eps_e) and _finite(eps) and float(eps) >= 0.0
    g_coh = g_coh_base and ((abs(float(eps)) < 1e-15) if strict_coh_zero else True)

    bar_rho = None
    bar_j = None
    rhs = None
    margin = None
    closes_e3 = False
    if (
        _is_theorem(mu_e)
        and _finite(mu)
        and _finite(xi)
        and _finite(c_r)
        and _finite(rho)
        and _finite(delta)
        and _finite(eps)
        and float(delta) > 0.0
    ):
        bar_rho = EPS_IDEMP + TAIL_PREFACTOR * float(xi)
        bar_j = float(c_r) * (float(rho) ** 2) / float(delta)
        rhs = bar_rho + bar_j + float(eps)
        margin = float(mu) - rhs
        closes_e3 = margin > 0.0

    g_m = g_x and g_r and g_n and g_coh and _is_theorem(mu_e) and closes_e3
    pass_base = g_x and g_r and g_n and g_coh and not missing_keys

    blockers = []
    if missing_keys:
        blockers.append(f"missing registry keys: {', '.join(missing_keys)}")
    if not g_x:
        blockers.append("G_X failed (xi_tail theorem/numeric/upper-bound)")
    if not g_r:
        blockers.append("G_R failed (c_r theorem/numeric/nonnegative)")
    if not g_n:
        blockers.append("G_N failed (rho_nf/delta_rec theorem/numeric/positive)")
    if not g_coh:
        blockers.append("G_Coh failed (eps_coh theorem/numeric/strict-coherence)")

    return {
        "pass": pass_base,
        "reason": "; ".join(blockers) if blockers else "",
        "gates": {"G_X": g_x, "G_R": g_r, "G_N": g_n, "G_Coh": g_coh, "G_M": g_m},
        "derived": {
            "bar_rho_pt_thm": bar_rho,
            "bar_j_w_thm": bar_j,
            "rhs_total": rhs,
            "epistemic_margin": margin,
            "closes_e3": closes_e3,
        },
        "inputs": {
            "xi_tail": xi,
            "c_r": c_r,
            "rho_nf": rho,
            "delta_rec": delta,
            "eps_coh": eps,
            "mu_strat": mu,
        },
    }


def _evaluate_functor(stitch_data: Dict[str, Any], eps_coh: Any) -> Dict[str, Any]:
    consts = stitch_data.get("constants")
    if not isinstance(consts, dict):
        return {
            "pass": False,
            "reason": "stitch constants missing constants object",
            "checks": {},
        }

    l_d_e = _entry(consts, "l_d_can")
    sigma_e = _entry(consts, "sigma_star_can")
    eta_e = _entry(consts, "eta_coh_star_can")

    l_d = l_d_e.get("value")
    sigma = sigma_e.get("value")
    eta = eta_e.get("value")

    c_l_d = _is_theorem(l_d_e) and _finite(l_d) and float(l_d) > 0.0
    c_sigma = _is_theorem(sigma_e) and _finite(sigma) and float(sigma) > 0.0
    c_eta = _is_theorem(eta_e) and _finite(eta) and float(eta) >= 0.0
    c_eta_sigma = c_eta and c_sigma and float(eta) < float(sigma)
    c_eps_match = _finite(eps_coh) and c_eta and abs(float(eta) - float(eps_coh)) < 1e-12

    ok = c_l_d and c_sigma and c_eta and c_eta_sigma and c_eps_match
    blockers = []
    if not c_l_d:
        blockers.append("l_d_can theorem/numeric/positive failed")
    if not c_sigma:
        blockers.append("sigma_star_can theorem/numeric/positive failed")
    if not c_eta:
        blockers.append("eta_coh_star_can theorem/numeric/nonnegative failed")
    if not c_eta_sigma:
        blockers.append("eta_coh_star_can < sigma_star_can failed")
    if not c_eps_match:
        blockers.append("eta_coh_star_can does not match registry eps_coh")

    return {
        "pass": ok,
        "reason": "; ".join(blockers) if blockers else "",
        "checks": {
            "l_d_can_ok": c_l_d,
            "sigma_star_can_ok": c_sigma,
            "eta_coh_star_can_ok": c_eta,
            "eta_lt_sigma_ok": c_eta_sigma,
            "eta_matches_eps_coh_ok": c_eps_match,
        },
        "inputs": {
            "l_d_can": l_d,
            "sigma_star_can": sigma,
            "eta_coh_star_can": eta,
        },
    }


def evaluate_formalism(
    registry_path: Path,
    stitch_path: Path,
    strict_coh_zero: bool,
    require_gm: bool,
) -> Dict[str, Any]:
    try:
        registry_data = _load_json(registry_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "pass": False,
            "reason": f"registry load failed: {exc}",
            "registry": str(registry_path),
            "stitch": str(stitch_path),
            "registry_eval": None,
            "functor_eval": None,
            "require_gm": require_gm,
            "strict_coh_zero": strict_coh_zero,
            "computed_at_utc": _now_iso(),
        }

    registry_eval = _evaluate_registry(registry_data, strict_coh_zero=strict_coh_zero)

    try:
        stitch_data = _load_json(stitch_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "pass": False,
            "reason": f"stitch constants load failed: {exc}",
            "registry": str(registry_path),
            "stitch": str(stitch_path),
            "registry_eval": registry_eval,
            "functor_eval": None,
            "require_gm": require_gm,
            "strict_coh_zero": strict_coh_zero,
            "computed_at_utc": _now_iso(),
        }

    eps_coh = registry_eval["inputs"].get("eps_coh")
    functor_eval = _evaluate_functor(stitch_data, eps_coh=eps_coh)

    pass_all = bool(registry_eval["pass"]) and bool(functor_eval["pass"])
    if require_gm:
        pass_all = pass_all and bool(registry_eval["gates"]["G_M"])

    reason_parts = []
    if not registry_eval["pass"]:
        reason_parts.append(f"object-level invariants failed: {registry_eval['reason']}")
    if not functor_eval["pass"]:
        reason_parts.append(f"functor-level invariants failed: {functor_eval['reason']}")
    if require_gm and not registry_eval["gates"]["G_M"]:
        reason_parts.append("G_M failed under require_gm=True")

    return {
        "pass": pass_all,
        "reason": "; ".join(reason_parts) if reason_parts else "",
        "registry": str(registry_path),
        "stitch": str(stitch_path),
        "registry_eval": registry_eval,
        "functor_eval": functor_eval,
        "require_gm": require_gm,
        "strict_coh_zero": strict_coh_zero,
        "computed_at_utc": _now_iso(),
    }


def _emit_violation(phase: str, script_name: str, report: Dict[str, Any], restored: bool = False) -> None:
    payload = {
        "guard": "FAIL",
        "phase": phase,
        "script": script_name,
        "registry_restored": restored,
        "report": report,
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)


def start_guard(
    script_name: str,
    registry_path_str: Optional[str] = None,
    strict_coh_zero: bool = True,
    require_gm: bool = False,
    mutate_registry: bool = False,
) -> GuardSession:
    registry_path = resolve_user_path(registry_path_str or DEFAULT_REGISTRY_REL)
    stitch_path = resolve_user_path(DEFAULT_STITCH_REL)

    report = evaluate_formalism(
        registry_path=registry_path,
        stitch_path=stitch_path,
        strict_coh_zero=strict_coh_zero,
        require_gm=require_gm,
    )
    if not report["pass"]:
        _emit_violation(phase="pre", script_name=script_name, report=report, restored=False)
        raise SystemExit(2)

    snapshot = registry_path.read_text() if (mutate_registry and registry_path.exists()) else None
    return GuardSession(
        script_name=script_name,
        registry_path=registry_path,
        stitch_path=stitch_path,
        strict_coh_zero=strict_coh_zero,
        require_gm=require_gm,
        mutate_registry=mutate_registry,
        registry_snapshot=snapshot,
    )


def finish_guard(session: GuardSession) -> Dict[str, Any]:
    report = evaluate_formalism(
        registry_path=session.registry_path,
        stitch_path=session.stitch_path,
        strict_coh_zero=session.strict_coh_zero,
        require_gm=session.require_gm,
    )
    if report["pass"]:
        return report

    restored = False
    if session.mutate_registry and session.registry_snapshot is not None:
        session.registry_path.write_text(session.registry_snapshot)
        restored = True

    _emit_violation(phase="post", script_name=session.script_name, report=report, restored=restored)
    raise SystemExit(2)

