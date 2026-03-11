# Extraction Specification — P vs NP Canonical Lane

## Objective

Replace manual constant assignment with a deterministic three-stage
pipeline that extracts, validates, promotes, and guards theorem-level
constants.

## Pipeline

```
  constants_extraction_inputs.json
            |
            v
  [1] extract_constants.py
            |
            v
  constants_extracted.json        (intermediate, validated)
            |
            v
  [2] promote_constants.py
            |
            +---> constants_registry.json   (updated)
            +---> stitch_constants.json     (updated)
            +---> promotion_report.json     (audit trail)
            |
            v
  [3] pn_closure_guard.py
            |
            v
  certificate_runtime.json        (8-gate evaluation)
```

## Raw Formulas

Seven constants are extracted from
`artifacts/constants_extraction_inputs.json`.

### Main Constants

| # | Name | Formula | Components | Constraint |
|---|------|---------|------------|------------|
| 1 | `lambda_def` | `lambda_raw` | lambda_raw = 1.0 | positive |
| 2 | `mu_def` | `mu_raw` | mu_raw = 1.0 | positive |
| 3 | `kappa_2sat` | `kappa_2sat_raw` | kappa_2sat_raw = 1.0 | positive |
| 4 | `kappa_planted` | `kappa_planted_raw` | kappa_planted_raw = 1.0 | positive |
| 5 | `kappa_occ3` | `kappa_occ3_raw` | kappa_occ3_raw = 1.0 | positive |
| 6 | `kappa_general` | `kappa_general_raw` | kappa_general_raw = 0.0 | nonneg |
| 7 | `eps_coh` | `eps_coh_raw` | eps_coh_raw = 0.0 | nonneg, strict_zero |

### Stitch Constants

| # | Name | Formula | Components | Constraint |
|---|------|---------|------------|------------|
| 1 | `sub_ledger_fraction` | `closed_classes / total_classes` | closed=3.0, total=4.0 | positive |

## Validation Rules

- **Positive:** Value must be strictly greater than zero.  Applied to
  lambda_def, mu_def, kappa_2sat, kappa_planted, kappa_occ3,
  sub_ledger_fraction.

- **Nonnegative:** Value must be >= 0.  Applied to kappa_general,
  eps_coh.

- **Strict zero:** Value must equal 0.0 exactly.  Applied to eps_coh
  (coherence residual must be zero for the identification (Cook–Levin)
  to hold without gap).

## Normalization

Each constant is divided by its reference value (default 1.0) to
produce a normalized value.  For the P vs NP lane, raw and normalized
values coincide because all references are 1.0.

## Output Artifacts

| File | Producer | Consumer |
|------|----------|----------|
| `artifacts/constants_extracted.json` | extract_constants.py | promote_constants.py |
| `artifacts/constants_registry.json` | promote_constants.py | pn_closure_guard.py |
| `artifacts/stitch_constants.json` | promote_constants.py | pn_closure_guard.py |
| `artifacts/promotion_report.json` | promote_constants.py | (audit) |
| `repro/certificate_runtime.json` | pn_closure_guard.py | THIRD_PARTY_RERUN_PROTOCOL |

## Constant Provenance

Each constant in the registry carries:

- `value` — Numeric value (or null for unresolved).
- `status` — `derived_numeric` (proved) or `normalized_placeholder` (OPEN).
- `theorem_level` — Boolean; true only when the underlying proof is complete.
- `source` — File reference(s) to the proof or definition.
- `source_section` — Specific section within the source.
- `formula` — Formula string used in extraction.
- `notes` — Human-readable provenance note.

## References

- `artifacts/constants_extraction_inputs.json` — Input manifest.
- `scripts/extract_constants.py` — Extraction script.
- `scripts/promote_constants.py` — Promotion script.
- `scripts/pn_closure_guard.py` — Closure guard.
