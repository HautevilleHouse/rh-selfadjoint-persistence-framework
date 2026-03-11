# The Riemann Hypothesis via Self-Adjoint Spectral Persistence
## Canonical Lane (defined term): the manifold-constrained local-to-global closure architecture for the RH program.

Canonical Lane research workspace for the Millennium Problem:

the distribution of the nontrivial zeros of the Riemann zeta function on the critical line.

## Main Manuscript

- [paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md](paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md)
- [paper/CANONICAL_ROUTING_INDEX.md](paper/CANONICAL_ROUTING_INDEX.md)

## Structure

- `paper/`
  - `RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md`

- `notes/`
  - `EG1_public.md`
  - `EG2_public.md`
  - `EG3_public.md`
  - `EG4_public.md`
  - `IDENTIFICATION_BRIDGE.md`

- `repro/`
  - `REPRO_PACK.md`
  - `THIRD_PARTY_RERUN_PROTOCOL.md`
  - `run_repro.sh`
  - `repro_manifest.json`
  - `certificate_baseline.json`

- `scripts/`
  - `rh_closure_drift_guard.py`
  - `rh_closure_registry.py`
  - `rh_closure_target_calculator.py`
  - `extract_rh_e3_margin.py`
  - `rh_formalism_guard.py`
  - `verify_manifest.py`

- `artifacts/`
  - `constants_registry.json`
  - `stitch_constants.json`
 
## Local Repro Command

```bash
bash repro/run_repro.sh
```

This writes `repro/certificate_runtime.json`.

## How To Read This Professionally

1. Theorem chain first: read `paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md`.
2. Constants provenance second: audit `paper/EXTRACTION_SPEC.md`, `artifacts/constants_registry.json`, and `artifacts/stitch_constants.json`.
3. Pipeline third: run `bash repro/run_repro.sh` to audit hashes/provenance/gates; it is reproducibility infrastructure, not theorem generation.

Current RH runner policy:

- `repro/run_repro.sh` writes `repro/certificate_runtime.json` and verifies `repro/repro_manifest.json` against the tracked files in the public rerun pack.

## Citation

- Metadata: [`CITATION.cff`](CITATION.cff).
- Manuscript target: [paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md](paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md)

## Authorship

- Program author: **HautevilleHouse**
- Canonical attribution source: [`CITATION.cff`](CITATION.cff)
