# Scripts

- `rh_closure_drift_guard.py`: canonical-lane closure gate evaluator for RH.
- `rh_formalism_guard.py`: object-level and functor-level invariant enforcer.
- `rh_closure_registry.py`: persistent registry manager for theorem-tagged constants.
- `extract_rh_e3_margin.py`: E3/epistemic margin quantity calculator.
- `rh_closure_target_calculator.py`: quantitative target threshold computer for G_M closure.
- `verify_manifest.py`: SHA-256 checker for `repro/repro_manifest.json`.

Guard inputs:

- `artifacts/constants_registry.json`
- `artifacts/stitch_constants.json`

Guard output:

- `repro/certificate_runtime.json`

Output schema includes:

- native gate keys (`G_X`, `G_R`, `G_N`, `G_Coh`, `G_M`),
- derived quantities (`bar_rho_pt_thm`, `bar_j_w_thm`, `epistemic_margin`),
- lane status (`manifold_constrained` / `raw_diagnostic`),
- strict pass flag: `all_pass`.
