#!/usr/bin/env python3
"""Verify SHA-256 entries in the RH repro manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = "repro/repro_manifest.json"


def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else PROJECT_ROOT / p


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--pretty", action="store_true")
    ns = ap.parse_args()

    manifest_path = _resolve(ns.manifest)
    data = json.loads(manifest_path.read_text())
    files = data.get("files", [])
    if not isinstance(files, list):
        raise ValueError("manifest files must be list")

    missing: list[str] = []
    mismatches: list[dict[str, str]] = []
    for ent in files:
        rel = ent["path"]
        actual_path = PROJECT_ROOT / rel
        if not actual_path.exists():
            missing.append(rel)
            continue
        actual = _sha256(actual_path)
        expected = ent["sha256"]
        if actual != expected:
            mismatches.append(
                {
                    "path": rel,
                    "expected": expected,
                    "actual": actual,
                }
            )

    out = {
        "ok": not missing and not mismatches,
        "manifest": str(manifest_path.relative_to(PROJECT_ROOT)),
        "missing": missing,
        "mismatches": mismatches,
    }
    if ns.pretty:
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, sort_keys=True))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
