# Nurok OpenAKB Troubleshooting

Read this reference when `nurok kb validate`, `nurok kb push`, or snapshot promotion fails.

## Failure Matrix

| Signal | Likely cause | Action |
| --- | --- | --- |
| `AKB001` | Duplicate ID across source and section objects | Mint stable unique IDs in the shared namespace. |
| `AKB002` | Section has neither content nor children | Add `content_uri` or at least one child. |
| `AKB003` | Content section has no source citation | Add non-empty `source_ids` referencing declared sources. |
| `AKB007` | Parent, source, discovery, citation, or local-link reference does not resolve | Correct the reference kind and target. |
| `AKB011` | Invalid ID, timestamp, URI, hash, language, or type | Fix the exact pointer; do not suppress validation. |
| `NUROK009: hosted URI is not the canonical path` | Content is outside Nurok's hosted layout | For Markdown, use `sections/<section-id>/content.md` and materialize it. |
| `NUROK015: captured_at is required` | Platform policy requires a capture time | Add a truthful RFC 3339 value to each non-redacted source. |
| `NUROK014` | Source type or pointer visibility is outside Nurok's vocabulary | Use a supported source type and visibility. |
| `NUROK007: natural key conflicts with another source` | Sources share a type plus URI | Deduplicate the corpus, rebuild, validate, and publish a corrected snapshot. |
| `cli.kb.manifest_unresolvable` | A local file is unsafe, outside the root, or missing without complete stamps | Materialize the file or correct the relative URI. |
| `cli.kb.push_no_create` | An unbound copy was pushed with `--no-create` | Remove the flag only for authorized creation, or resolve the existing target. |
| `conflict.already_exists` during implicit create | The owner already has the slug but the copy is unbound | Resolve and verify the existing KB instead of creating again. |
| `dependency.timeout` after uploads | Finalize or indexing exceeded a gateway deadline | Inspect the named draft and resume only when retry is safe. |
| Push fails after `--sync-metadata` | Record metadata may have changed before snapshot creation or promotion failed | Re-read the KB record, compare the saved baseline, and report or explicitly revert the partial change. |
| Authentication I/O error in a sandbox | Credential storage is outside allowed access | Request narrowly scoped permission for Nurok credentials. |

## Canonical Working-Copy Rules

- Use `sections/<section-id>/content.md` for Markdown.
- Give every non-redacted source a recognized type and RFC 3339 `captured_at`.
- Keep relative paths canonical, inside the working copy, and symlink-safe.
- Remember that local files override declared stamps because push re-derives their hashes.
- Treat stamps-only missing files as partial copies; push can still fail if the server requests an absent blob.
- Keep descriptor, manifest, and blob sizes within CLI and server caps.

Use the bundled audit for natural-key collisions because offline structural validation may lack server inventory context.

## Understand Push State

Default `nurok kb push` loads and stamps the copy, runs preflight, resolves or creates a target, writes a new namespace when needed, creates a draft, uploads missing blobs, and promotes to merge. Preserve the snapshot ID after draft creation.

After a timeout, inspect the snapshot:

- `merged`: verify; do not promote again.
- `finalized` or `approved`: choose the next transition deliberately.
- `draft` plus retryable timeout: resume with the current `descriptor_version` after checking progress.
- `draft` plus validation errors: repair locally and create a corrected snapshot.
- deleted, superseded, or unknown: inspect history and do not guess.

For local deployments, correlate API, knowledge-base, and search logs around the request. Decreasing unprocessed counts can show useful progress; healthy containers alone do not prove the operation fits gateway timeouts.

## Use Flags Deliberately

| Flag | Use |
| --- | --- |
| `--message` | Record the revision change. |
| `--draft` | Upload without promotion. |
| `--finalize` | Validate and freeze without merge. |
| `--approve` | Record owner approval. |
| `--expected-revision` | Refuse to overwrite a moved live revision. |
| `--base` | Select a specific base snapshot. |
| `--sync-metadata` | Patch record metadata before snapshot creation; re-check the record after any later failure. |
| `--no-create` | Forbid implicit creation. |
| `--no-verify` | Use only for explicit diagnostics, never routine publication. |

Completion requires valid local artifacts, a merged/live revision, the intended remote record, relevant retrieval, and an explicit disposition for failed drafts.
