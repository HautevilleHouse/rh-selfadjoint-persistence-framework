# Reviewer Map

## Claim Scope
- Canonical-lane claim: inside the `manifold_constrained` lane, if the theorem chain in this repository holds and the guard certificate passes, the repository-level RH closure claim is satisfied.
- Classical mapping claim: carried by the in-repo bridge theorems; independent validation is performed via public reruns and expert review.

## Theorem Dependency Chain
1. `EG1`: projected coercivity / structural floor.
2. `EG2`: capture + flow/restart invariance.
3. `EG3`: finite-restart spacing (no Zeno cascade).
4. `EG4`: compactness-rigidity and endpoint identification.
5. Scalar closure: `G_X, G_R, G_N, G_Coh, G_M` all `PASS`.

Primary files:
- `paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md`
- `notes/EG1_public.md`
- `notes/EG2_public.md`
- `notes/EG3_public.md`
- `notes/EG4_public.md`
- `notes/IDENTIFICATION_BRIDGE.md`

## Falsification Conditions
- `repro/certificate_runtime.json` has any non-`PASS` gate.
- `lane.active_lane != "manifold_constrained"`.
- `all_pass != true`.
- Any manifest hash mismatch under `repro/repro_manifest.json`.
- A verified counterexample to any EG theorem statement used in the paper.

## Reproducibility Check
Run:

```bash
bash repro/run_repro.sh
```

Then verify:

```bash
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path("repro/certificate_runtime.json").read_text())
assert d.get("all_pass") is True
assert d.get("lane",{}).get("active_lane") == "manifold_constrained"
for g in ["G_X","G_R","G_N","G_Coh","G_M"]:
    assert d["gates"].get(g) == "PASS", g
print("OK")
PY
```
