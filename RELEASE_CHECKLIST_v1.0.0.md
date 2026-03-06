# Release Checklist (`v1.0.0`)

Use this checklist before creating any formal public milestone.

## Gate 1: Repository Hygiene

- [ ] Working tree is clean:

```bash
git status --short
```

- [ ] Main branch is current:

```bash
git fetch origin
git log --oneline --decorate -n 5
```

## Gate 2: Canonical-Lane Repro Pass

- [ ] Run canonical-lane certificate:

```bash
bash repro/run_repro.sh
```

- [ ] Confirm strict pass:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p=Path("repro/certificate_runtime.json")
d=json.loads(p.read_text())
assert d.get("all_pass") is True, "all_pass != true"
assert d.get("lane",{}).get("active_lane")=="manifold_constrained"
print("OK: all_pass=true, active_lane=manifold_constrained")
PY
```

- [ ] Record runtime certificate hash:

```bash
shasum -a 256 repro/certificate_runtime.json
```

## Gate 3: Metadata + Citation

- [ ] `CITATION.cff` title and URL are current.
- [ ] README citation section points to the main manuscript path.
- [ ] License is present and correct (`LICENSE`).

## Gate 4: Signing Setup (one-time)

- [ ] Confirm signing key exists:

```bash
gpg --list-secret-keys --keyid-format LONG
```

- [ ] Ensure Git uses signing key for tags:

```bash
git config gpg.program gpg
git config user.signingkey 18F50064C8B1EE1E
git config tag.gpgsign true
```

- [ ] Ensure key is uploaded to GitHub (for Verified badges):

```bash
gh auth refresh -h github.com -s write:gpg_key
gpg --armor --export 18F50064C8B1EE1E > /tmp/release_signing_key.asc
gh gpg-key add /tmp/release_signing_key.asc
```

## Gate 5: Signed Tag + GitHub Release

- [ ] Create signed tag:

```bash
git tag -s v1.0.0 -m "v1.0.0"
```

- [ ] Push branch and tag:

```bash
git push origin main
git push origin v1.0.0
```

- [ ] Publish GitHub release:

```bash
gh release create v1.0.0 \
  --repo HautevilleHouse/rh-selfadjoint-persistence-framework \
  --title "v1.0.0" \
  --notes "Canonical-lane release: theorem notes, reproducibility pack, and baseline certificate."
```

## Gate 6: Zenodo DOI Snapshot

- [ ] Zenodo account connected to GitHub.
- [ ] Repository enabled in Zenodo integration.
- [ ] Verify DOI minted for `v1.0.0` release snapshot.
- [ ] Add DOI badge + DOI link to `README.md`.

## Post-Release Policy (mandatory)

- [ ] Do not force-push `main` after `v1.0.0`.
- [ ] Any changes go through new commits and new version tags (`v1.0.1`, `v1.1.0`, ...).
- [ ] Keep release artifacts immutable for external reproducibility.
