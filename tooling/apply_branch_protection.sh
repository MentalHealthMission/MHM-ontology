#!/usr/bin/env bash
set -euo pipefail

# Apply branch protection to `main` using GH_ADMIN_TOKEN from env or .env
# Requirements:
# - gh CLI installed
# - Admin token with Administration: Read and write on this repo

here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)

# Load .env if present (and not in CI)
if [ -f "$root/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$root/.env"
  set +a
fi

if [ -z "${GH_ADMIN_TOKEN:-}" ]; then
  echo "Error: GH_ADMIN_TOKEN is not set. See .env.example."
  exit 1
fi

repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Applying protection to $repo:main"

# Discover latest check names from a recent PR (fallback to defaults)
default_checks=(check-syntax profile-dl validate-units validate-sosa validate-skos validate-prov)
sha="$(gh api repos/$repo/commits --jq '.[0].sha' | head -n1 || true)"
checks_json=""
if [ -n "$sha" ]; then
  mapfile -t checks < <(GH_TOKEN="$GH_ADMIN_TOKEN" gh api repos/$repo/commits/$sha/check-runs --jq '.check_runs[].name' -H 'Accept: application/vnd.github+json' 2>/dev/null || true)
fi
if [ ${#checks[@]:-0} -eq 0 ]; then
  checks=("${default_checks[@]}")
fi
for c in "${checks[@]}"; do
  checks_json+="{\"context\": \"$c\"},"
done
checks_json="${checks_json%,}"

read -r -d '' BODY <<JSON
{
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false
  },
  "required_status_checks": {
    "strict": true,
    "checks": [ $checks_json ]
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false
}
JSON

GH_TOKEN="$GH_ADMIN_TOKEN" gh api -X PUT repos/$repo/branches/main/protection --input - -H 'Accept: application/vnd.github+json' <<<"$BODY" >/dev/null
echo "Protection applied. Verifying:"
GH_TOKEN="$GH_ADMIN_TOKEN" gh api repos/$repo/branches/main/protection --jq '{admins:.enforce_admins,required_reviews:.required_pull_request_reviews.required_approving_review_count,strict:.required_status_checks.strict,checks:(.required_status_checks.checks[]?.context)}'

