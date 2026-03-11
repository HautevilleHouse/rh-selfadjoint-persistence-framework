# Public Reproducibility Pack (Canonical Lane)

## Objective
Provide a local, hash-locked rerun path for the RH closure gate certificate.

## Included Artifacts
1. `repro_manifest.json`,
2. `run_repro.sh`,
3. baseline output `certificate_baseline.json`,
4. `THIRD_PARTY_RERUN_PROTOCOL.md`.

## Runner
From repository root:

```bash
bash repro/run_repro.sh
```

This executes:

```bash
python3 scripts/rh_closure_drift_guard.py --strict-coh-zero --registry artifacts/constants_registry.json --stitch artifacts/stitch_constants.json --out repro/certificate_runtime.json --history repro/drift_guard_runs.jsonl --pretty
python3 scripts/verify_manifest.py --manifest repro/repro_manifest.json --pretty
```

Runner note: `repro/run_repro.sh` also copies `artifacts/stitch_constants.json` and `artifacts/constants_registry.json` into `.codex_tmp/rh_closure/` for guard-module compatibility.

## Pass Criteria
1. `repro/certificate_runtime.json` exists,
2. gate states are `G_X=G_R=G_N=G_Coh=G_M=PASS`,
3. `all_pass` is `true`,
4. lane is `manifold_constrained`,
5. manifest verification reports `"ok": true`.

## Current Runtime Snapshot

At current registry state:

- `G_X=G_R=G_N=G_Coh=G_M=PASS`,
- `all_pass = true`,
- lane = `manifold_constrained`,
- manifest verification = `ok`.
