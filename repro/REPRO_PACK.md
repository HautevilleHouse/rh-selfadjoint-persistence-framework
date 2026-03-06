# Public Reproducibility Pack (Canonical Lane)

## Objective
Provide relative-path, hash-locked reruns of the canonical theorem-lane closure certificate.

## Included Artifacts
1. `repro_manifest.json` (SHA-256 hashes for runner, constants, manuscript, and certificate snapshot),
2. `run_repro.sh` (one-command relative-path runner),
3. baseline output at `repro/certificate_baseline.json`,
4. `THIRD_PARTY_RERUN_PROTOCOL.md` (attestation workflow).

## Runner
From repository root:

```bash
bash repro/run_repro.sh
```

This executes:

```bash
python3 scripts/rh_closure_drift_guard.py --strict-coh-zero --registry artifacts/constants_registry.json --stitch artifacts/stitch_constants.json --out repro/certificate_runtime.json --history repro/drift_guard_runs.jsonl --pretty
```

Runner note: `repro/run_repro.sh` also copies `artifacts/stitch_constants.json` and
`artifacts/constants_registry.json` into `.codex_tmp/rh_closure/` for guard-module compatibility.

## Pass Criteria
1. command completes without path edits,
2. output file `repro/certificate_runtime.json` is written,
3. gate states are `G_X=G_R=G_N=G_Coh=G_M=PASS`,
4. `all_pass` is `true`,
5. lane is `manifold_constrained`,
6. gate tuple and lane match `repro/certificate_baseline.json`.

## Runtime Certificate Hash
After rerun:

```bash
shasum -a 256 repro/certificate_runtime.json
```

## Canonical-Lane Status
XG6 is treated as closed on this lane: relative-path runner + hash manifest are now in-tree.
