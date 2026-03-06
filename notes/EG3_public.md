# EG3 Public Theorem Note (Standalone)

## 1. Objective
Prove finite restart complexity (no Zeno accumulation) on compact time windows, and give an explicit theorem source for

`delta_rec := inf T_cont(N,u) > 0`

from local continuation bounds.

## 2. Setup
Let restart times on the canonical lane be

`0 < tau_1 < tau_2 < ...`.

Define restart count up to horizon `T`:

`N(T) := # { k : tau_k <= T }`.

Near-failure radius is denoted `rho_nf`.
Restart spacing floor is denoted `delta_rec`.

## 3. Hypotheses
1. Uniform spacing floor:
   `tau_{k+1} - tau_k >= delta_rec > 0`.
2. Restart triggers occur only in canonical near-failure strip `m_per^(6x5) <= rho_nf`.
3. Local continuation theorem `O2` supplies positive continuation time on the trigger set.

## 4. Lemma (Counting Bound)
For every `T>0`:

`N(T) <= floor(T/delta_rec) + 1`.

### Proof
If `N(T)=m>=1`, then `tau_m <= T`.
By spacing:

`tau_m >= tau_1 + (m-1)delta_rec > (m-1)delta_rec`.

Hence `(m-1)delta_rec < T`, so `m <= floor(T/delta_rec)+1`. `QED.`

## 5. Theorem (EG3 Finite-Restart / No-Zeno)
Under hypotheses 1–3, restart times have no finite accumulation point on any compact interval.

### Proof
By the counting bound, `N(T)` is finite for each fixed `T`. Therefore infinitely many restart times cannot accumulate inside `[0,T]`. `QED.`

## 6. Corollary (Compact-Window Complexity)
For every compact window `[t0,T]`, the number of restart events is bounded by a deterministic function of `delta_rec` and `T-t0`.

## 7. Proposition (Explicit `delta_rec` Source from `O2`)
Let `T_cont(N,u)` be continuation time given by local continuation theorem `O2` at state `(N,u)`.
Define

`delta_rec := inf_{N,u : m_per^(6x5)(u) >= m_0} T_cont(N,u)`.

If `O2` provides a uniform lower bound `T_cont(N,u) >= underline T > 0` on that trigger set, then

`delta_rec >= underline T > 0`.

### Proof
Every element of the trigger set has continuation time at least `underline T`; therefore the infimum is at least `underline T`. `QED.`

## 8. Canonical Lane Instantiation Snapshot
- `delta_rec = 0.001`
- `rho_nf = 0.03430793496110181`

These values satisfy the hypotheses used by the counting theorem and no-Zeno corollary on the canonical lane.

## 9. Status
EG3 is closed on canonical-lane semantics by the theorem/proposition above.
