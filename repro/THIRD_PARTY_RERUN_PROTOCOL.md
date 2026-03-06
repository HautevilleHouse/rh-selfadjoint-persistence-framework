# Third-Party Rerun Protocol (XG7)

## Purpose
Provide a concrete attestation workflow for independent reruns of the canonical lane closure certificate.

## Inputs
- repository snapshot containing:
  - `scripts/rh_closure_drift_guard.py`,
  - `scripts/extract_rh_e3_margin.py`,
  - `scripts/rh_formalism_guard.py`,
  - `artifacts/constants_registry.json`,
  - `artifacts/stitch_constants.json`,
  - `repro/repro_manifest.json`,
  - `repro/certificate_baseline.json`.

## Rerun Command
```bash
bash repro/run_repro.sh
```

## Runtime Hash Command
```bash
shasum -a 256 repro/certificate_runtime.json
```

## Required Checks
1. produced file `repro/certificate_runtime.json`,
2. compatibility bootstrap files exist:
   - `.codex_tmp/rh_closure/stitch_constants.json`
   - `.codex_tmp/rh_closure/constants_registry.json`
3. lane field:
   - `"active_lane": "manifold_constrained"`,
4. gate tuple:
   - `G_X=PASS`, `G_R=PASS`, `G_N=PASS`, `G_Coh=PASS`, `G_M=PASS`,
5. strict status field:
   - `"all_pass": true`,
6. manifest hash match for runner/constants scripts.

## Attestation Template
Record and publish:

- date/time (UTC),
- machine + Python version,
- repository snapshot hash (or commit),
- certificate SHA-256,
- gate tuple,
- `all_pass` boolean value,
- pass/fail outcome.

Example statement:

`Independent rerun completed on <UTC>. certificate SHA-256=<hash>. Gate tuple PASS/PASS/PASS/PASS/PASS on manifold_constrained lane. all_pass=true.`

## Canonical-Lane Status
XG7 is considered closed in this manuscript by explicit invitation protocol + baseline hash comparability.
