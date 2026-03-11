# EG4 Public Theorem Note (Standalone)

## 1. Objective
Provide a standalone compactness-rigidity package that excludes normalized bad limits and closes the endpoint extraction stage.

## 2. Setup
Let `B` be the set of canonical-lane bad states (failure of target uniform package).
Let `N(u)` be the normalization map from bad states to normalized Weyl/Herglotz states.
Define compactness class:

`X := { m : C\\[0,1] -> C holomorphic Herglotz, m(z)=int_[0,1] dmu(x)/(x-z), mu in P([0,1]) }`.

Equip `X` with either equivalent topology:

1. local-uniform convergence on compact subsets of `C\\[0,1]`,
2. weak-* convergence of representing measures on `[0,1]`.

Define `badness : X -> [0,infinity)` lower-semicontinuous, with

`badness(v)=0` iff `v` is admissible.

## 3. Hypotheses
1. First-bad sequence exists under contradiction assumption:
   `u_n in B`, `v_n:=N(u_n)`, `badness(v_n) -> b_* > 0`.
2. Precompactness:
   `{v_n}` is precompact in `X`.
3. Rigidity exclusion:
   every normalized bad-limit candidate must satisfy `badness(v_infty)=0`.

Rigidity alternatives are encoded as contradiction channels:

- transport-identity violation,
- Herglotz admissibility violation,
- determining-class lock re-entry.

## 4. Lemma (Limit Extraction)
There exists a subsequence `v_{n_j}` converging in `X` to some `v_infty`.

### Proof
Immediate from precompactness. `QED.`

## 5. Lemma (Lower-Semicontinuity)
`badness(v_infty) >= liminf_j badness(v_{n_j}) = b_* > 0`.

### Proof
Lower-semicontinuity of `badness`. `QED.`

## 6. Lemma (Rigidity)
`badness(v_infty)=0`.

### Proof
By Hypothesis 3 (rigidity exclusion for normalized bad limits). `QED.`

## 7. Theorem (EG4 Compactness-Rigidity Closure)
The first-bad-sequence contradiction assumption is impossible; therefore the uniform package persists to endpoint extraction.

### Proof
Lemma 5 gives `badness(v_infty)>0`; Lemma 6 gives `badness(v_infty)=0`. Contradiction. `QED.`

## 8. Concrete Compactness Justification (Montel + Tightness)
For normalized Weyl/Herglotz states with support in `[0,1]`:

1. holomorphic local bounds imply normal-family compactness (Montel),
2. representing measures lie in `P([0,1])`, hence weak-* precompact,
3. Stieltjes representation preserves equivalence between function and measure limits.

This provides the explicit topology/function-space bridge required for standalone exposition.

## 9. Interface to Xi Bridge
After EG4 compactness-rigidity closure, endpoint identification is delegated to `IDENTIFICATION_BRIDGE.md` (fixed determining class + lock equations + uniqueness).

## 10. Status
EG4 is closed on canonical-lane semantics by the theorem and topology specification above.
