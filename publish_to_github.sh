#!/usr/bin/env bash
set -euo pipefail

if [[ "${ALLOW_REMOTE_PUBLISH:-0}" != "1" ]]; then
  echo "Remote publish is disabled by local-only policy."
  echo "This project is configured for laptop-local work."
  echo "If you intentionally want to publish, run with:"
  echo "  ALLOW_REMOTE_PUBLISH=1 $0 <owner> <repo> [public|private]"
  exit 1
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <owner> <repo> [public|private]"
  exit 1
fi

OWNER="$1"
REPO="$2"
VISIBILITY="${3:-public}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .git ]]; then
  git init -b main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Initial public release"
fi

if [[ "$VISIBILITY" == "private" ]]; then
  gh repo create "${OWNER}/${REPO}" --private --source=. --remote=origin --push
else
  gh repo create "${OWNER}/${REPO}" --public --source=. --remote=origin --push
fi

echo "Published: https://github.com/${OWNER}/${REPO}"
