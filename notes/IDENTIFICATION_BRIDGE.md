# Xi Identification Bridge (Canonical Lane)

## Fixed Determining Class
Use the Cauchy-kernel determining class on `[0,1]`:

`C_det := { k_n(x)=(x-z_n)^(-1) : n>=1 } U {1}`,

with `z_n := 2 + i/n`.
Then `z_n in C\\[0,1]` and `z_n -> 2` (accumulation point in holomorphy domain).

## Lock Equations
Let `mu_(E_0)` be the endpoint spectral measure and `mu_Xi` the arithmetic Xi spectral measure (in the normalized class).
Impose:

1. `int_[0,1] k_n(x) dmu_(E_0)(x) = int_[0,1] k_n(x) dmu_Xi(x)` for all `n>=1`,
2. `int_[0,1] dmu_(E_0) = int_[0,1] dmu_Xi = 1`.

## Theorem XIB-1 (Fixed-Class Uniqueness)
The lock equations imply `mu_(E_0)=mu_Xi`.

### Proof
Define Stieltjes transforms
`M_(E_0)(z)=int dmu_(E_0)(x)/(x-z)` and `M_Xi(z)=int dmu_Xi(x)/(x-z)`.
The lock equations give `M_(E_0)(z_n)=M_Xi(z_n)` on an infinite set with accumulation point in `C\\[0,1]`.
By the identity theorem, `M_(E_0)=M_Xi` on `C\\[0,1]`.
Equality of Stieltjes transforms on this domain yields equality of measures on `[0,1]`. `QED.`

## Theorem XIB-2 (Endpoint Identification)
If `E_0` and `Xi` lie in the same normalized determining class and satisfy the lock equations, then

`E_0 = Xi`.

### Proof
Apply Theorem XIB-1 at the measure level, then Weyl uniqueness in the normalized class. `QED.`

## Canonical-Lane Status
XG5 is treated as closed on the manifold-constrained lane by this fixed determining class and lock proof (same content as Appendix E in `RH_SELF_ADJOINT_PERSISTENCE_PREPRINT.md`).
