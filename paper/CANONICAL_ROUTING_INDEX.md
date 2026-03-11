# Canonical Routing Index (RH)

This file is the single routing map for where each proof package lives in:

- main preprint sections,
- mirror note files,
- certificate/artifact keys.

## Gate Routing

| Gate | Main preprint location | Mirror note | Registry/artifact key(s) |
|---|---|---|---|
| `G_X` (tail extraction) | `Section 13.43/13.53M` | `notes/EG1_public.md` | `xi_tail` |
| `G_R` (response constant) | `Section 13.53P.8` | `notes/EG2_public.md` | `c_r` |
| `G_N` (near-failure/spacing) | `Section 13.53P.8` | `notes/EG3_public.md` | `rho_nf`, `delta_rec` |
| `G_Coh` (strict coherence) | `Section 13.53P.8.3` | `notes/IDENTIFICATION_BRIDGE.md` | `eps_coh` |
| `G_M` (final epistemic margin) | `Section 13.53M/13.53O` | derived | all above keys + `mu_strat` |

## Repro Routing

| Artifact | Path |
|---|---|
| Runner | `repro/run_repro.sh` |
| Drift guard | `scripts/rh_closure_drift_guard.py` |
| Formalism guard | `scripts/rh_formalism_guard.py` |
| Runtime certificate | `repro/certificate_runtime.json` |
| Baseline certificate | `repro/certificate_baseline.json` |
| Registry | `artifacts/constants_registry.json` |
| Stitch constants | `artifacts/stitch_constants.json` |
| Third-party rerun protocol | `repro/THIRD_PARTY_RERUN_PROTOCOL.md` |
