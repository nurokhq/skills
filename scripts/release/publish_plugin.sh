#!/usr/bin/env bash
# Called only by the gated main-branch CI job; uploads no data to OpenAI.
set -euo pipefail

: "${PLUGIN_VERSION:?PLUGIN_VERSION is required}"
: "${GITHUB_SHA:?GITHUB_SHA is required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
if [[ "${GITHUB_EVENT_NAME:-}" != "push" || "${GITHUB_REF:-}" != "refs/heads/main" ]]; then
  echo "Plugin publication is restricted to main-branch push runs" >&2
  exit 1
fi
if [[ ! "$PLUGIN_VERSION" =~ ^0\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid plugin release version" >&2
  exit 1
fi
if [[ "$(git rev-parse HEAD)" != "$GITHUB_SHA" ]]; then
  echo "Checkout does not match the requested release commit" >&2
  exit 1
fi

# Compare against the newest release, not only the previous commit: a queued
# docs-only push must still publish skills from an earlier skipped CI run.
tag="nurok-v$PLUGIN_VERSION"
git fetch origin 'refs/tags/nurok-v*:refs/tags/nurok-v*'
previous_tag=$(git tag --list 'nurok-v*' --sort=-version:refname | head -n 1)
if [[ -n "$previous_tag" ]]; then
  if ! git merge-base --is-ancestor "$previous_tag" HEAD; then
    echo "A newer or divergent plugin release already exists; skipping this run."
    exit 0
  fi
  # The current tag may belong to an interrupted draft. Let the release-state
  # check below validate it before deciding whether publication can continue.
  if [[ "$previous_tag" != "$tag" ]] && git diff --quiet "$previous_tag" HEAD -- \
    'plugins/nurok-kb/skills/**' packaging/nurok scripts/release LICENSE; then
    # An earlier interrupted run may have left a draft that unchanged inputs
    # would otherwise abandon; stop loudly instead of reporting success.
    drafts=$(gh release list --limit 100 --json tagName,isDraft | python3 -c '
import json
import sys

releases = json.load(sys.stdin)
print(" ".join(
    release["tagName"] for release in releases
    if release["isDraft"] and release["tagName"].startswith("nurok-v")
))
')
    if [[ -n "$drafts" ]]; then
      echo "Unpublished plugin draft(s) need recovery: $drafts" >&2
      echo "Rerun the release job that created each draft, or delete the draft." >&2
      exit 1
    fi
    echo "Plugin inputs are unchanged since $previous_tag."
    exit 0
  fi
fi

archive="nurok-$PLUGIN_VERSION.zip"
python3 - <<'PY'
import hashlib
import json
import os
from pathlib import Path

version = os.environ["PLUGIN_VERSION"]
metadata = json.loads(Path(f"dist/nurok-{version}.build.json").read_bytes())
if metadata["source_commit"] != os.environ["GITHUB_SHA"] or metadata["dirty"]:
    raise SystemExit("Package provenance does not match the clean release commit")
if metadata["version"] != version:
    raise SystemExit("Package version does not match the release")
archive = Path(f"dist/nurok-{version}.zip")
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
expected = f"{digest}  {archive.name}\n"
if archive.with_suffix(".zip.sha256").read_text() != expected:
    raise SystemExit("Package checksum does not match the archive")
if metadata["archive_sha256"] != digest:
    raise SystemExit("Package provenance checksum does not match the archive")
PY

# An interrupted upload can leave a draft. Resume only that commit's draft;
# published assets are immutable and must never be overwritten.
if gh release view "$tag" --json isDraft,targetCommitish > dist/release-state.json; then
  python3 - <<'PY'
import json
import os
from pathlib import Path

release = json.loads(Path("dist/release-state.json").read_bytes())
if not release["isDraft"] or release["targetCommitish"] != os.environ["GITHUB_SHA"]:
    raise SystemExit("Existing release is published or targets another commit")
PY
else
  cat > dist/release-notes.md <<EOF_NOTES
Nurok read-only knowledge workflows using bundled skills and remote MCP.

Source commit: $GITHUB_SHA

Download the ZIP and its SHA-256 checksum. The build JSON records the source
commit and each packaged file's digest. See the
[release guide](https://github.com/$GITHUB_REPOSITORY/blob/$GITHUB_SHA/packaging/nurok/README.md)
for setup, compatibility, and public-directory submission requirements.

This GitHub release is a distribution artifact, not an OpenAI directory publication.
EOF_NOTES
  gh release create "$tag" --draft --target "$GITHUB_SHA" \
    --title "Nurok $PLUGIN_VERSION" --notes-file dist/release-notes.md
fi

gh release upload "$tag" "dist/$archive" "dist/$archive.sha256" \
  "dist/nurok-$PLUGIN_VERSION.build.json" --clobber
gh release edit "$tag" --draft=false --latest
