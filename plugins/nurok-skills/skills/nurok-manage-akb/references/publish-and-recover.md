# Publish And Recover

Read this reference before creating or changing remote Nurok state, or when a prior push left a snapshot or draft.

## Inspect The Environment

Use the endpoint selected by the user. A common local configuration is:

```bash
export NUROK_WEB_URL="http://127.0.0.1:3000/"
export NUROK_API_URL="http://127.0.0.1:8333/"
```

Inspect the CLI, endpoint, and authentication before mutation:

```bash
nurok --version
nurok config show --output json --pretty
nurok status --output json --pretty
```

Require Nurok CLI 0.2.0 or later and inspect `nurok kb push --help` before relying on mutating flags. State whether the API is local, staging, or production. An expired access token may refresh during push; a missing authenticated session is a blocker. Redact tokens, API keys, credential-store paths, and sensitive headers from all output and reports.

## Publish A New KB

Use create mode only when the user authorized a new remote KB, the descriptor is unbound, and read-only checks found no intended existing target. Validate the publishing copy immediately before push:

```bash
nurok kb validate --dir <publishing-copy> --output json --pretty
```

Then publish:

```bash
nurok kb push \
  --dir <publishing-copy> \
  --message "<specific initial revision>" \
  --output json \
  --pretty
```

A namespaceless descriptor pushed without `--kb` implicitly creates a private KB for the authenticated owner and writes the namespace back before snapshot publication. Preserve that binding even if a later upload or promotion step fails. If the owner already has the slug, resolve the existing record instead of retrying implicit creation.

## Publish An Existing KB

Require verified local and remote identity. Run record-aware validation immediately before mutation:

```bash
nurok kb validate \
  --kb <owner/slug> \
  --dir <publishing-copy> \
  --output json \
  --pretty
```

Then use the same explicit target, forbid creation, and guard the recorded live revision:

```bash
nurok kb push \
  --kb <owner/slug> \
  --dir <publishing-copy> \
  --no-create \
  --expected-revision <live-revision> \
  --message "<specific change>" \
  --output json \
  --pretty
```

Add `--sync-metadata` only when descriptor metadata should patch the record. It runs before snapshot creation and is not rolled back when a later upload or promotion step fails. Capture the metadata baseline before using it and re-read the record on every failure. Omit `--expected-revision` only when no live revision exists or the user explicitly authorizes an unguarded update. Do not use `--draft`, `--finalize`, or `--approve` unless the requested workflow requires that lifecycle boundary.

Capture the endpoint, KB ID, owner/slug, snapshot ID, descriptor version, revision, state, and warnings. Do not end while an upload or promotion process is still running.

## Recover A Failed Publication

Separate the failure by lifecycle boundary:

1. If the failed push used `--sync-metadata`, re-read the KB record and compare it with the saved baseline. Record metadata may have changed even when no draft or live revision exists. Preserve or revert that partial change only with user authorization.
2. If no draft exists, fix the local, validation, identity, or authentication error and revalidate.
3. If a draft exists, inspect it before any new push:

   ```bash
   nurok kb snapshot list --kb <owner/slug> --limit 100 --output json --pretty
   nurok kb snapshot get <snapshot-id> --output json --pretty
   ```

4. If it is merged, verify the KB and do not promote it again.
5. If it is finalized or approved, choose only the required next transition.
6. If it remains draft after a retryable timeout, establish idempotency and progress, then resume the same snapshot:

   ```bash
   nurok kb snapshot promote <snapshot-id> \
     --to merge \
     --message "<change summary>" \
     --expected-version <descriptor-version> \
     --output json \
     --pretty
   ```

7. If server validation rejected content, repair and validate the working copy, then create a corrected snapshot.
8. Stop repeated promotion attempts when state and service evidence show no progress.

Do not delete a pre-existing draft. Delete an invalid draft created during the current task only after a successful replacement and only when the user-authorized workflow permits cleanup.

## Verify Completion

```bash
nurok kb show --kb <owner/slug> --output json --pretty
nurok kb search --kb <owner/slug> "<representative query>" --limit 3 --output json --pretty
```

Require the intended owner/slug, KB ID, visibility, live state, returned revision, metadata, and relevant search result. Page through `nurok kb source pointers` with a limit no greater than 100 and follow the cursor to EOF when pointer visibility is part of the task.

Reconcile server-written namespace and stamps into both maintained copies and validate again when local artifacts changed. Report IDs, revision, merge state, counts, tests, validations, retrieval evidence, metadata status, pointer status, warnings, retained drafts, and uncommitted local files. Claim visual verification only when a browser was actually used.
