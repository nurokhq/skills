# Nurok OpenAKB Troubleshooting

Read this reference when validation, publication, metadata synchronization, or snapshot recovery fails.

## Re-Discover The Failed Command

Record the installed version and inspect help for the failed command and each nested lifecycle command:

```bash
nurok --version
nurok kb --help
nurok kb <command> --help
```

Use the actual result to identify current flags, conflicts, output fields, recovery hints, and state transitions. Do not apply a flag sequence or default behavior remembered from another CLI version.

## Diagnose Stable Validation Signals

| Signal | Likely cause | Action |
| --- | --- | --- |
| `AKB001` | Duplicate typed ID under case-insensitive comparison | Preserve one stable identity and mint a valid unique typed ID for the other entity. |
| `AKB002` | Section has neither content nor children | Add `content_uri` or at least one child. |
| `AKB003` | Content section has no Source citation | Add non-empty `source_ids` containing declared `SRC-` IDs. |
| `AKB004` | Section parent graph contains a cycle | Repair `parent_id` edges without changing unrelated stable IDs. |
| `AKB007` | A local typed reference does not resolve | Correct the target while preserving Source-versus-Section kind. |
| `AKB010` | A reference uses `SEC-` where a Source is required or `SRC-` where a Section is required | Replace it with an ID of the required entity kind. |
| `AKB011` | Invalid typed ID, slug, timestamp, URI, hash, language, type, or case-insensitive array uniqueness | Fix the exact pointer; do not suppress validation. |
| Hosted Markdown path is not canonical | Content is outside Nurok's hosted layout | Use `sections/<section-id>/content.md` and materialize it. |
| Capture time is required | A non-redacted Source lacks persisted-capture time | Add a truthful RFC 3339 `captured_at`; do not use discovery or attempt time. |
| Source natural key conflicts | Sources share a type plus canonical URI | Deduplicate the corpus, preserve the intended Source ID, rebuild, and validate. |
| Local manifest or payload cannot resolve | A local file is unsafe, outside the root, missing, or lacks complete stamps | Materialize the file or correct the relative URI without traversing outside the working copy. |
| Target already exists during creation | The intended remote KB exists but the Descriptor is unbound | Resolve and verify the existing KB instead of creating again. |
| Timeout after upload or lifecycle mutation | The server may have advanced state after the client stopped waiting | Re-read the record and snapshot before any retry. |
| Publication fails after metadata work | Record metadata may have changed independently of snapshot state | Compare both saved baselines with current remote state before retry or revert. |
| Authentication I/O error in a sandbox | Credential storage is outside allowed access | Request narrowly scoped permission for Nurok credentials. |

## Apply Canonical Working-Copy Rules

- Use typed Source IDs (`SRC-` plus six ASCII base36 characters) and Section IDs (`SEC-` plus six ASCII base36 characters); resolve and deduplicate them case-insensitively.
- Use `sections/<section-id>/content.md` for Nurok-hosted Markdown.
- Give every non-redacted Source a recognized type and truthful RFC 3339 `captured_at`.
- Keep relative paths canonical, inside the working copy, and symlink-safe.
- Treat a prior hash or length as stale after changing the bytes it describes.
- Treat stamps-only missing files as partial copies; restore a blob unless its availability at the verified target or base is established.
- Distinguish Source `content_length` from Section `content_length` and `provenance_length`; do not use `capture_length`.
- Keep Descriptor, manifest, and blob sizes within both OpenAKB schema caps and the target deployment's actual caps.

Use the bundled audit for local path, stamp, natural-key, typed-ID, and citation-reference checks. Use the current OpenAKB validator and CLI for full structural, content, sidecar, inline-citation, platform-policy, and deployment-cap validation.

## Recover From Observed State

Do not assume what the publication command did before failure. Re-read:

- remote KB identity, record metadata, visibility, and live revision;
- all relevant snapshots and their current states and versions;
- local `openakb.json`, its diff, and the generator source of truth;
- working-copy bytes and integrity data;
- the failed command's structured output and recovery hints.

Inspect the current lifecycle help and choose only a supported working-copy-aware recovery operation. If a matching draft is resumable, verify its target, Descriptor, blob completeness, and drift guards before reusing it. If it is already live, verify rather than advancing it again. If it contains invalid content, repair and revalidate locally before creating a corrected snapshot. Stop repeated attempts when remote state shows no progress.

Do not hardcode metadata defaults, lifecycle flags, command conflicts, pull or push write-back behavior, cap cache details, JSON envelopes, or pagination paths in this skill. The installed CLI defines those execution details.

Completion requires valid local artifacts, the intended remote record and live revision, verified record metadata and visibility, relevant retrieval evidence, reconciled local Descriptor state, and an explicit disposition for failed or retained drafts.
