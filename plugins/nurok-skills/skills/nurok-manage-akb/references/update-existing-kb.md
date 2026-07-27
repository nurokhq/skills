# Update An Existing KB

Read this reference whenever a namespace, owner/slug, KB ID, or existing remote record identifies the target.

## Acquire The Working Copy

When the target is remote and no maintained local working copy exists, detach it into a new destination:

```bash
nurok kb pull \
  --kb <owner/slug> \
  --dir <working-copy> \
  --output json \
  --pretty
```

Do not reconstruct an existing KB from search results or metadata. Before refreshing an existing destination, inventory local changes: pull refreshes `openakb.json` from the server and refuses to overwrite changed artifacts unless `--force` is used. Never use `--force` without explicit authority to replace the named local files.

## Establish The Baseline

Resolve the target with `nurok kb show` and record:

- KB ID, owner/slug, state, visibility, and live revision;
- title, description, summary, prompts, tags, and language;
- local namespace and descriptor ID;
- source, section, root, content, and integrity-stamp counts;
- source and publishing copy locations;
- active or failed draft snapshots associated with the update.

Inspect revision and snapshot history rather than inferring it from the current record:

```bash
nurok kb changelog --kb <owner/slug> --limit 100 --output json --pretty
nurok kb snapshot list --kb <owner/slug> --limit 100 --output json --pretty
```

Follow pagination cursors to EOF when the first page is full or reports a next cursor.

Require local and remote identity to agree before mutation. Preserve live KB visibility unless the user explicitly requests a change.

## Plan The Delta

Reapply the scope and curation rules to every candidate source. Record included, excluded, and held counts; existing-topic mappings; proposed sections; structural migrations; metadata changes; provenance changes; and unexpected count changes.

Preserve stable IDs, namespace, capture times, content boundaries, and unchanged hashes. If scope or taxonomy changes, update `AKB.md` before the generator. Avoid unrelated crawler, corpus, taxonomy, and formatting changes.

## Update Metadata And Visibility

Keep title, description, summary, prompts, category descriptions, and generated content consistent. Use `--sync-metadata` during publication only when record-owned metadata should change. This flag patches the record before snapshot creation and is not transactional with upload or promotion. Preserve the baseline metadata and re-read the record after any failed push to identify partial success.

Treat source pointer visibility and KB visibility independently. Descriptor declarations do not automatically repair owner source-registry values. When registry correction is required, page through `nurok kb source list` with a limit no greater than 100, follow `meta.pagination.cursor.next_cursor` to EOF, and update only mismatches:

```bash
nurok kb source update <source-id> \
  --visibility public \
  --output json \
  --compact
```

Collect per-source failures. Publish a new revision after registry changes because the existing revision is not rewritten automatically. Never make the KB public merely because its sources are public.

When the user explicitly authorizes a KB visibility change, apply it independently, normally after a successful publication:

```bash
nurok kb visibility <public-or-private> \
  --kb <owner/slug> \
  --output json \
  --pretty
```

Verify the returned owner/slug and visibility. Do not expect `--sync-metadata` or source pointer updates to change KB visibility.

## Protect Generated Integrity

A generator can emit authoring-form JSON and remove stamps written by an earlier push. Inspect existing `guide_hash`, `guide_length`, `content_hash`, `content_length`, provenance stamps, and namespace before regeneration.

- When bytes are unchanged, preserve their existing hashes and lengths through structured updates.
- When content changes, compare old and new aggregate hashes and explain the delta.
- Do not treat count equality as proof of content equality.
- Do not overwrite a server-stamped descriptor with a namespaceless generated copy.

## Synchronize The Publishing Copy

Derive the publishing set from the descriptor. Include `openakb.json` and every relative local blob referenced by `guide_uri`, section `content_uri` or `provenance_uri`, a `file` source `uri`, source `capture_uri`, or `x.ai.nurok.skill_uri`. The common simple set is `openakb.json`, `AKB.md`, and `sections/`, but it is not a complete allowlist. Do not copy unreferenced crawler code, raw archives, tests, caches, build notes, or virtual environments.

Copy only changed artifacts, confirm source and publishing artifacts are byte-identical before push, and validate both copies. After a successful push writes namespace or integrity data, reconcile the server-stamped descriptor back into the generator-preserved source copy without losing corpus-owned changes.

## Require Update Evidence

Before publication, validate the publishing copy with `--kb <owner/slug>` and require valid local artifacts, a verified remote target, intended metadata, preserved visibility, stable identity, reviewed taxonomy changes, and a specific revision message. During publication, use `--no-create`; use the recorded live revision as `--expected-revision` whenever one exists, unless the user explicitly authorizes an unguarded update.

After publication, require the intended live revision and metadata, unchanged visibility unless authorized, expected source pointer projections, representative retrieval, and a report of any retained drafts or local differences.
