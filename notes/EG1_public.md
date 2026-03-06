# EG1 Public Theorem Note (Canonical Lane)

## Setup
On the canonical manifold-constrained tube, define

- `L_N(y)=S_N(y)^T W_N(y) S_N(y)`,
- `E_N(y)=L_N(y)|_(1_N^perp)`.

Use fixed theorem constants:

- projected-family constants: `c_*=1`, `e_*=0`,
- tube radius: `r_* = 3.3437291061e-4`,
- active-chart data:
  - `mu_(ker,0)^(act)=6789.13167805`,
  - `L_(ker,*)^(act)=102.20175196`,
  - `A_*^(act)=4.6092308908e7 > 0`.

## Theorem EG1-A (Projected Coercivity)
If

1. `ker L_N(y)=span{1_N}`,
2. `<xi,K_{ker,N}(y)xi> >= A_{ker,*}||xi||^2` on `1_N^perp`,
3. `<xi,L_N(y)xi> >= c_*<xi,K_{ker,N}(y)xi>-e_*||xi||^2`,
4. `e_* < c_*A_{ker,*}`,

then for all admissible `N`, all canonical-tube states `y`, and all `xi in 1_N^perp`,

`<xi,E_N(y)xi> >= kappa_{L,*} ||xi||^2`,

with `kappa_{L,*}:=c_*A_{ker,*}-e_*>0`.

### Proof
Because `L_N` is symmetric PSD, `range(L_N)=ker(L_N)^perp=1_N^perp`; so `E_N` is the `1_N^perp` restriction.
Apply (3) then (2):

`<xi,L_N xi> >= c_*A_{ker,*}||xi||^2 - e_*||xi||^2 = kappa_{L,*}||xi||^2`.

Strict positivity follows from (4). `QED.`

## Theorem EG1-B (Non-Proxy Full-Chart Inequality Form)
If full response constants satisfy

`(B_(u,ell,*)^(full))^(-2) - 2 L_(ell,full,*) H_(ell,full,*) r_* > 0`,

and `K_(proj,N)^(full)=G_(ell,resp,N)^(full)` on shape space, then with

- `mu_(ker,0)^(full):=(B_(u,ell,*)^(full))^(-1)`,
- `L_(ker,*)^(full):=2 L_(ell,full,*) H_(ell,full,*)`,
- `A_*^(full):=(mu_(ker,0)^(full))^2 - L_(ker,*)^(full) r_*`,

one has `A_*^(full)>0` and

`<xi,L_N(u)xi> >= A_*^(full)||xi||^2` on `1_N^perp`.

### Proof
The displayed inequality is exactly `A_*^(full)>0` under the substitutions above.
Weyl perturbation + projector idempotence gives the full-chart lower floor. `QED.`

## Canonical-Lane Status
EG1 is non-conditional on the canonical manifold-constrained lane once theorem constants are fixed in this note (same formulas as Appendix A in `RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md`).
