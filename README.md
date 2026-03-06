# The Riemann Hypothesis via Self-Adjoint Spectral Persistence
## Canonical Lane (defined term): Restart-Compatible Continuation and Closure

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18876071.svg)](https://doi.org/10.5281/zenodo.18876071)

Public repository for the manuscript, theorem notes, and reproducibility artifacts.

## Main Manuscript

- [paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md](paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md)

## Suggested GitHub Metadata

- Description: `Riemann Hypothesis via self-adjoint spectral persistence, with Canonical Lane closure, standalone theorem notes, and reproducibility artifacts.`
- Topics: `riemann-hypothesis`, `number-theory`, `spectral-theory`, `self-adjoint-operators`, `mathematical-proof`, `reproducibility`

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

- `artifacts/`
  - `constants_registry.json`
  - `stitch_constants.json`

## Citation

- Use metadata in [`CITATION.cff`](CITATION.cff).
- Suggested citation target:
  - [paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md](paper/RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md)

## Authorship

- Program author: **HautevilleHouse**
- Canonical attribution source: [`CITATION.cff`](CITATION.cff)

## Release Discipline

- Use [RELEASE_CHECKLIST_v1.0.0.md](RELEASE_CHECKLIST_v1.0.0.md) before any formal public milestone/tag.

## License

- This repository is licensed under the [MIT License](LICENSE).

## Note

`run_repro.sh` assumes repo-relative paths. If you upload this as a standalone repo, keep the same directory names (`scripts/`, `repro/`, `artifacts/`) or adjust paths in the runner accordingly.

`repro/certificate_runtime.json` is a runtime artifact (git-ignored) produced after running `bash repro/run_repro.sh`.
