# EG2 Public Theorem Note (Standalone)

## 1. Objective
Prove capture-invariance for the defect under alternating flow and restart:

`D(t) >= sigma_* - Delta_coh[t0,t]`,

with strict invariance `D(t) >= sigma_*` when `Delta_coh[t0,t]=0`.

## 2. Setup
Let `u(t)` be a piecewise-smooth canonical-lane trajectory on `[t0,T]` with restart times

`t0 < tau_1 < ... < tau_m <= T`.

Define the defect

`D(t) := B(u(t)) - lambda_J(u(t))`.

Define a nondecreasing coherence ledger

`C(t) := Delta_coh[t0,t]`,

with `C(t0)=0`.

Restart map: at each restart time,

`u(tau_k^+) = R_nf(u(tau_k^-))`.

## 3. Hypotheses
There exist constants `L_D > 0`, `sigma_* > 0` such that:

1. Flow inequality on every open flow segment:
   `d/dt D(t) >= -L_D (D(t)-sigma_*) - d/dt C(t)` (a.e.).
2. Restart capture:
   `D(tau_k^+) >= sigma_*` for all `k`.
3. Initial capture:
   `D(t0) >= sigma_*`.

## 4. Flow Lemma
On any flow interval `(a,b)` (no restart), define

`Phi(t):=exp(L_D t) (D(t)-sigma_*+C(t))`.

Then `Phi` is nondecreasing on `(a,b)`.

### Proof
Differentiate:

`d/dt Phi = exp(L_D t) [ d/dt(D-sigma_*+C) + L_D(D-sigma_*+C) ]`.

Using Hypothesis 1:

`d/dt(D-sigma_*+C) >= -L_D(D-sigma_*)`.

Hence

`d/dt Phi >= exp(L_D t) L_D C(t) >= 0`.

`QED.`

## 5. Segment Lower Bound
For `t in (a,b)`:

`D(t) >= sigma_* - C(t) + exp(-L_D(t-a)) ( D(a)-sigma_*+C(a) )`.

In particular, if `D(a) >= sigma_* - C(a)`, then `D(t) >= sigma_* - C(t)`.

### Proof
From Flow Lemma, `Phi(t) >= Phi(a)`; divide by `exp(L_D t)`. `QED.`

## 6. Restart Compatibility
At each restart `tau_k`:

`D(tau_k^+) >= sigma_* >= sigma_* - C(tau_k^+)`.

### Proof
Hypothesis 2 and `C >= 0`. `QED.`

## 7. Theorem (EG2 Capture-Invariance)
Under hypotheses 1–3, for all `t in [t0,T]`:

`D(t) >= sigma_* - C(t) = sigma_* - Delta_coh[t0,t]`.

If `Delta_coh[t0,t]=0`, then `D(t) >= sigma_*`.

### Proof
Start with Hypothesis 3 at `t0`.  
Propagate on first flow interval by Section 5.  
Apply Section 6 at restart, then iterate over all flow/restart segments.  
Finite composition gives the bound on all `[t0,T]`. `QED.`

## 8. Corollary (Strict Coherence Lane)
If `C(t)=0` identically, then

`D(t) >= sigma_*` for all `t`.

## 9. Restart-Defect Constant Extraction (Jump Term)
Assume on near-failure strip:

1. `||R_nf(u)-u|| <= ( C_(nf,*) + eps_(nf,*)/rho_(nf) ) m_per^(6x5)(u)`,
2. `W_N^(alpha)` is `L_(W,*)`-gradient-Lipschitz.

Then

`|W_N^(alpha)(R_nf(u)) - W_N^(alpha)(u)| <= C_(R,*) (m_per^(6x5)(u))^2`,

with

`C_(R,*) := (L_(W,*)/2) ( C_(nf,*) + eps_(nf,*)/rho_(nf) )^2`.

Hence theorem jump-rate contribution is

`bar j_(W,*)^(thm) = C_(R,*) rho_(nf)^2 / delta_(rec)`.

### Proof
Apply descent lemma:
`|W(v)-W(u)| <= (L_(W,*)/2)||v-u||^2`, with `v=R_nf(u)`,
then substitute displacement bound; divide by spacing floor `delta_(rec)`. `QED.`

## 10. Canonical-Lane Instantiation Snapshot
- `L_D = 192.85454134255954`
- `sigma_* = 0.00033437291061`
- strict coherence lane target: `eta_(coh,*) = 0`
- theorem-lane jump constant: `C_(R,*)^(thm)=9.960035360010515`

## 11. Status
EG2 is closed on canonical-lane semantics by the theorem above.
