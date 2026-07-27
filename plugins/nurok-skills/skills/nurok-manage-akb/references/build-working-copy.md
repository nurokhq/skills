# Build Or Repair A Working Copy

Read this reference when creating `openakb.json`, repairing AKB artifacts, or changing metadata, sections, sources, content, or generation logic.

## Scaffold A New Working Copy

For a new KB, use the CLI's known-good offline scaffold instead of recreating the base descriptor by hand:

```bash
nurok kb init \
  --dir <working-copy> \
  --id <stable-id> \
  --title "<literal title>" \
  --description "<concise description>" \
  --output json \
  --pretty
```

Run this only for an authorized new local destination. It refuses to overwrite scaffold files; do not work around that protection. Replace the generated guide with `assets/AKB.template.md` only after defining the KB-specific scope contract, then update the descriptor and content through the declared source of truth.

## Define Audience Metadata

Use a literal subject-specific title. Write a concise description covering the corpus, provenance, scope, and major topics without exposing scraper implementation details. Keep the Nurok summary aligned unless the user requests different copy:

```json
{
  "title": "<Subject> Knowledge Base",
  "description": "<Corpus, provenance, scope, and major topics>",
  "x": {
    "ai.nurok": {
      "summary": "<Same value as description>",
      "suggested_prompts": ["<Corpus-grounded synthesis question>"]
    }
  }
}
```

Define four to eight ordered prompts. Make each answerable from the corpus, natural, distinct, useful for synthesis or comparison, unique, and no longer than 300 characters. Do not claim coverage the corpus lacks.

## Build The Descriptor

- Use `$schema: https://schema.openakb.org/v1/openakb.schema.json`.
- Keep source and section IDs unique in one shared namespace, lowercase, stable, and at most 64 characters. Add a stable digest when truncating.
- Preserve an existing `namespace`; it binds the working copy to its remote owner.
- Give every category and section a non-empty description.
- Omit `parent_id` from root categories. Keep child relationships valid and intentional.
- Give every content section at least one valid `source_ids` citation.
- Use `sections/<section-id>/content.md` for hosted Markdown content.
- Add truthful RFC 3339 `captured_at` values to every non-redacted source.
- Use supported Nurok source types: `feed`, `file`, `firsthand`, `redacted`, or `url`.
- Use `feed` plus `discovered_via_id` when a feed or listing discovered content.
- Deduplicate by the source natural key, normally source type plus canonical URI.
- Keep relative local URIs canonical, rooted inside the working copy, and safe through symlinks.
- Reject absolute paths, parent traversal, and symlinks that resolve outside the working-copy root.

For public evidence intended for audience citation, declare pointer visibility on each applicable source:

```json
{
  "x": {
    "ai.nurok": {
      "pointer_visibility": "public"
    }
  }
}
```

Do not infer KB record visibility from source visibility.

## Keep Generation Deterministic

Change the corpus-owned generator or declared source of truth rather than only editing generated JSON. Keep canonical derived files separate when the original corpus uses another layout.

- Reuse capture timestamps for unchanged sources.
- Preserve stable source and section IDs across rebuilds.
- Define metadata, prompts, taxonomy, and pointer extensions once in the generator.
- Preserve `guide_hash`, `guide_length`, `content_hash`, `content_length`, and provenance stamps when bytes are unchanged.
- Compare aggregate content hashes before and after regeneration.
- Regenerate `AKB.md` or `sections/` only when their inputs or declared convention changed.

Add focused tests for exact metadata and prompt order, prompt constraints, category descriptions, valid parent and source references, pointer declarations, stable namespace, stable timestamps, deterministic output, and corpus-specific counts or deduplication invariants.

## Audit And Validate

Run the bundled supplemental audit:

```bash
python3 <skill-dir>/scripts/audit_working_copy.py --dir <working-copy>
```

Fix every error and review every warning. A stamps-only warning is valid only when the target or base snapshot already has that blob; restore the local file before creating a new KB or whenever blob availability is uncertain.

Then run the project generator and focused tests and rebuild once to check stability. Treat the Nurok CLI as authoritative for descriptor, content, policy, path, and cap validation. For a new unbound working copy, run:

```bash
nurok kb validate --dir <working-copy> --output json --pretty
```

For a verified existing KB, include its explicit owner/slug so record-dependent identity and metadata checks run:

```bash
nurok kb validate \
  --kb <owner/slug> \
  --dir <working-copy> \
  --output json \
  --pretty
```

Require `ok: true` with no error-severity issues. Do not use `--no-verify` to bypass descriptor, content, policy, path, or cap failures.
