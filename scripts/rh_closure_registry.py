#!/usr/bin/env python3
"""Persistent registry for RH closure constants.

This script makes the final-margin inputs auditable and non-optional.
It stores required constants in one JSON file, validates completeness/theorem tags,
and computes the E3 margin from the same source of truth.
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

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_ARTIFACT_DIR = ".codex_tmp/rh_closure"
DEFAULT_REGISTRY_REL = f"{DEFAULT_ARTIFACT_DIR}/constants_registry.json"
DEFAULT_MARGIN_REL = f"{DEFAULT_ARTIFACT_DIR}/margin_from_registry.json"
LEGACY_REGISTRY_REL = ".codex_tmp/rh_closure_constants_registry.json"

REQUIRED_KEYS = (
    "xi_tail",
    "c_r",
    "rho_nf",
    "delta_rec",
    "eps_coh",
    "mu_strat",
)


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _entry(value: float | None, source: str, theorem_level: bool, notes: str = "") -> Dict[str, Any]:
    return {
        "value": value,
        "source": source,
        "theorem_level": theorem_level,
        "notes": notes,
    }


def default_registry() -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "updated_at_utc": _now_iso(),
        "constants": {
            "xi_tail": _entry(None, "", False, "Set Xi_(tail,*)^(thm) once proved."),
            "c_r": _entry(None, "", False, "Set C_(R,*)^(thm) once extracted."),
            "rho_nf": _entry(None, "", False, "Set rho_(nf)^(thm) once extracted."),
            "delta_rec": _entry(None, "", False, "Set delta_(rec)^(thm) once extracted."),
            "eps_coh": _entry(
                0.0,
                "13.53P.8.3 strict canonical normalization",
                True,
                "Strict canonical branch closure sets eps_(coh,*)^(thm)=0.",
            ),
            "mu_strat": _entry(None, "", False, "Set mu_(strat,*)^(thm) once branch-global theorem value is fixed."),
        },
    }


def load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text())
    if "constants" not in data or not isinstance(data["constants"], dict):
        raise ValueError("Invalid registry format: missing 'constants' object")
    return data


def save_registry(path: Path, data: Dict[str, Any]) -> None:
    data["updated_at_utc"] = _now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def resolve_user_path(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def ensure_registry_present(path: Path, requested_rel: str) -> None:
    """Backfill canonical registry from legacy path when needed."""
    if path.exists():
        return
    if requested_rel != DEFAULT_REGISTRY_REL:
        return
    legacy = resolve_user_path(LEGACY_REGISTRY_REL)
    if not legacy.exists():
        return
    data = load_registry(legacy)
    save_registry(path, data)


def set_values(data: Dict[str, Any], args: argparse.Namespace) -> None:
    consts = data["constants"]
    for key in REQUIRED_KEYS:
        value = getattr(args, key)
        if value is None:
            continue
        if key not in consts:
            consts[key] = _entry(None, "", False, "")
        consts[key]["value"] = value
        if args.source is not None:
            consts[key]["source"] = args.source
        if args.theorem_level is not None:
            consts[key]["theorem_level"] = bool(args.theorem_level)
        if args.notes is not None:
            consts[key]["notes"] = args.notes


def validate(data: Dict[str, Any], require_theorem: bool) -> Dict[str, Any]:
    consts = data["constants"]
    missing = []
    non_numeric = []
    non_theorem = []
    for key in REQUIRED_KEYS:
        entry = consts.get(key)
        if not isinstance(entry, dict):
            missing.append(key)
            continue
        value = entry.get("value")
        if value is None:
            missing.append(key)
            continue
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            non_numeric.append(key)
        if require_theorem and not bool(entry.get("theorem_level", False)):
            non_theorem.append(key)
    ok = not missing and not non_numeric and (not require_theorem or not non_theorem)
    return {
        "ok": ok,
        "missing": missing,
        "non_numeric": non_numeric,
        "non_theorem": non_theorem,
    }


def compute_margin(data: Dict[str, Any]) -> Dict[str, Any]:
    consts = data["constants"]
    vals = {k: consts[k]["value"] for k in REQUIRED_KEYS}
    result = compute(
        xi_tail=float(vals["xi_tail"]),
        c_r=float(vals["c_r"]),
        rho_nf=float(vals["rho_nf"]),
        delta_rec=float(vals["delta_rec"]),
        eps_coh=float(vals["eps_coh"]),
        mu_strat=float(vals["mu_strat"]),
        mu_star=None,
        c_psi=None,
        m0=None,
    )
    out = {
        "computed_at_utc": _now_iso(),
        "inputs": vals,
        "result": {
            "bar_rho_pt_thm": result.bar_rho_pt_thm,
            "bar_j_w_thm": result.bar_j_w_thm,
            "rhs_total": result.rhs_total,
            "epistemic_margin": result.epistemic_margin,
            "closes_e3": result.closes_e3,
            "xi_tail_max_if_mu_strat_given": result.xi_tail_max_if_mu_strat_given,
            "jump_rate_max_if_mu_strat_given": result.jump_rate_max_if_mu_strat_given,
        },
    }
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--file",
        default=DEFAULT_REGISTRY_REL,
        help=f"Registry JSON path (default: {DEFAULT_REGISTRY_REL})",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Create registry template if missing.")

    p_set = sub.add_parser("set", help="Set one or more constants in the registry.")
    for key in REQUIRED_KEYS:
        p_set.add_argument(f"--{key.replace('_', '-')}", dest=key, type=float, default=None)
    p_set.add_argument("--source", default=None, help="Common source string for provided keys.")
    p_set.add_argument(
        "--theorem-level",
        dest="theorem_level",
        type=int,
        choices=(0, 1),
        default=None,
        help="Set theorem_level for provided keys (1=true, 0=false).",
    )
    p_set.add_argument("--notes", default=None, help="Common notes string for provided keys.")

    p_check = sub.add_parser("check", help="Validate required constants.")
    p_check.add_argument(
        "--require-theorem",
        action="store_true",
        help="Also require theorem_level=true for all required constants.",
    )

    p_comp = sub.add_parser("compute", help="Compute margin from registry constants.")
    p_comp.add_argument("--pretty", action="store_true", help="Pretty-print output JSON.")
    p_comp.add_argument(
        "--out",
        default=DEFAULT_MARGIN_REL,
        help="Write computation JSON to this path.",
    )
    p_comp.add_argument(
        "--require-theorem",
        action="store_true",
        help="Require theorem-level tags before computing.",
    )

    return p


def main() -> None:
    parser = build_parser()
    ns = parser.parse_args()
    path = resolve_user_path(ns.file)
    ensure_registry_present(path, ns.file)

    if ns.cmd == "init":
        existed = path.exists()
        if existed:
            data = load_registry(path)
        else:
            data = default_registry()
            save_registry(path, data)
        print(json.dumps({"status": "ok", "file": str(path), "created": not existed}, sort_keys=True))
        return

    guard_session = start_guard(
        script_name=Path(__file__).name,
        registry_path_str=ns.file,
        strict_coh_zero=True,
        require_gm=False,
        mutate_registry=(ns.cmd == "set"),
    )

    data = load_registry(path)

    if ns.cmd == "set":
        set_values(data, ns)
        save_registry(path, data)
        finish_guard(guard_session)
        print(json.dumps({"status": "ok", "file": str(path)}, sort_keys=True))
        return

    if ns.cmd == "check":
        report = validate(data, require_theorem=bool(ns.require_theorem))
        finish_guard(guard_session)
        print(json.dumps(report, indent=2, sort_keys=True))
        raise SystemExit(0 if report["ok"] else 2)

    if ns.cmd == "compute":
        report = validate(data, require_theorem=bool(ns.require_theorem))
        if not report["ok"]:
            print(json.dumps(report, indent=2, sort_keys=True))
            raise SystemExit(2)
        out = compute_margin(data)
        finish_guard(guard_session)
        out_path = resolve_user_path(ns.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        if ns.pretty:
            print(json.dumps(out, indent=2, sort_keys=True))
        else:
            print(json.dumps(out, sort_keys=True))
        return

    raise SystemExit(1)


if __name__ == "__main__":
    main()
