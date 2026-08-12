# Publish And Recover

Read this reference before creating or changing remote Nurok state, or when a prior publication left a snapshot or draft.

## Inspect The Environment And CLI

Use the endpoint selected by the user. Before mutation, inspect the installed CLI and every candidate command:

```bash
nurok --version
nurok --help
nurok kb --help
nurok kb <command> --help
```

Continue through nested help for lifecycle commands. Use the current CLI's supported diagnostics to verify the effective API endpoint and authenticated identity without exposing credentials. State whether the API is local, staging, or production. Redact tokens, API keys, credential-store paths, and sensitive headers from all output and reports.

Do not assume command names, flags, defaults, conflicts, output envelopes, metadata behavior, recovery entry points, or Descriptor write-back behavior from an earlier CLI release. If the current surface cannot enforce the required target, create/update, drift, and recovery guardrails, stop the mutation and report the missing capability.

## Prepare Every Mutation

Before invoking a remote mutation:

1. Confirm publish authority, effective endpoint, authenticated owner, `kb_identity`, lifecycle mode, and intended visibility.
2. Save the remote record, live revision, record metadata, relevant snapshot state, local `openakb.json`, generator source of truth, and working-copy diff.
3. Inspect help for the exact validate, publish, metadata, snapshot, source-registry, and visibility operations needed.
4. Determine whether the command may create a KB, overwrite files, write Descriptor identity or stamps, synchronize record metadata, or advance lifecycle state.
5. Compare every Source block with its included article-body ranges, verify every page-chrome exclusion against structural evidence, require the bundled audit to pass against both copies and their Descriptor projections, validate the publishing copy with the current CLI, and resolve all content-integrity and error-severity results.

Never bypass original-content comparison or validation to evade Descriptor, content, path, policy, or deployment-cap errors.

## Publish A New KB

Use create mode only when the user authorized a new remote KB, the Descriptor is unbound, and read-only checks found no intended existing target. Use only the create or publish workflow documented by the installed CLI.

Before execution, verify how the current command selects or creates the target and what it writes back to `openakb.json`. After execution or failure, re-read and diff the Descriptor. Preserve any verified remote binding written during a partially successful operation. If the intended owner already has the target slug, resolve that existing record instead of retrying creation.

## Publish An Existing KB

Require verified local and remote identity. Select the target explicitly through the form supported by the current CLI. Require its create-prevention guard and use its concurrency, revision, or version guard against the recorded baseline.

Decide separately whether remote record metadata should change. Inspect current help to determine whether metadata synchronization is part of publication or a separate operation. Save the record baseline because metadata and snapshot publication may not be transactional. After any failure, re-read the record before deciding whether to retry, preserve, or explicitly revert a partial metadata change.

Capture the endpoint, KB ID, owner/slug, snapshot identity, Descriptor version, revision, state, local Descriptor diff, and warnings from the actual results. Do not end while an upload or promotion process is still running.

## Recover A Failed Publication

Use observed remote and local state, not a memorized flag sequence:

1. Re-read the KB record, record metadata, live revision, local Descriptor, and known snapshot state.
2. Inspect the current snapshot lifecycle and publication command help, including nested recovery commands.
3. List and inspect relevant snapshots using the current output and pagination structure. Verify target, state, version, Descriptor, and blob completeness before mutation.
4. If no draft exists, repair the local, validation, identity, authorization, or authentication error and revalidate.
5. If a matching resumable draft exists, prefer the current CLI's working-copy-aware resume path. Do not create a duplicate draft merely because the original command failed.
6. Before resuming, verify that the working copy still matches the draft and that the current command offers the necessary idempotency and version or drift guard.
7. Advance only the required next lifecycle transition. If the snapshot is already live or merged, verify completion and do not promote it again.
8. If server validation rejected content, repair and revalidate the working copy before creating any corrected snapshot.
9. Stop repeated attempts when state and service evidence show no progress.

Write published namespace, revision, hash, or length data back to the maintained local source only when the recovered remote result and working-copy bytes agree. Do not delete a pre-existing draft. Delete an invalid draft created during the current task only when the authorized workflow permits cleanup and a successful replacement is verified.

## Verify Completion

Use the current CLI's supported read operations to verify:

- intended endpoint, owner/slug, KB ID, visibility, and live state;
- returned live revision and remote record metadata;
- snapshot state and absence or explicit retention of failed drafts;
- representative section retrieval or search evidence;
- representative retrieved Section text matching the validated presentation-formatted original content;
- source pointer projections when they are in scope;
- actual post-command `openakb.json` changes.

Follow pagination using the structured fields actually returned by the installed CLI. Reconcile verified server-written namespace and stamps into each maintained copy and validate again when local artifacts changed. Report IDs, revision, lifecycle state, counts, tests, validations, retrieval evidence, metadata status, pointer status, warnings, retained drafts, and uncommitted local files. Claim visual verification only when a browser was actually used.
