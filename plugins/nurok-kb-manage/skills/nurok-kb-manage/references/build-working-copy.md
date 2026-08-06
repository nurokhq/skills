# Build Or Repair A Working Copy

Read this reference when creating `openakb.json`, repairing KB artifacts, or changing metadata, sections, sources, content, or generation logic.

## Scaffold A New Working Copy

For a new KB, inspect the installed CLI and use its supported offline scaffold instead of recreating the base descriptor by hand:

```bash
nurok --version
nurok kb --help
nurok kb init --help
```

Use only options shown by the installed help. Run the scaffold only for an authorized new local destination, inspect its overwrite behavior before execution, and do not work around protections. Replace the generated guide with `assets/AKB.template.md` only after defining the KB-specific scope contract, then update the descriptor and content through the declared source of truth.

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
- Keep top-level Descriptor `id` and `namespace` as `[a-z0-9_-]` slugs of at most 64 characters.
- Give every Source an ID matching `SRC-[0-9A-Za-z]{6}` and every Section an ID matching `SEC-[0-9A-Za-z]{6}`. Compare IDs case-insensitively in one shared identity space. Prefer uppercase prefixes with lowercase bodies when minting IDs.
- Preserve an existing `namespace`; it binds the working copy to its remote owner.
- Give every category and section a non-empty description.
- Omit `parent_id` from root categories. Require every `parent_id` to resolve to a Section and keep the parent graph acyclic.
- Give every section with `content_uri` at least one `source_ids` citation. Require each entry to be a Source ID, unique case-insensitively, and resolved to a declared Source.
- Use `sections/<section-id>/content.md` for hosted Markdown content.
- Treat `content_type` as optional with the OpenAKB default `text/markdown`; do not make it mandatory because of a CLI or consumer implementation.
- Require `discovered_via_id` to resolve to a Source. Require local link `section_id` and provenance-sidecar `section_id` to resolve to a Section; require sidecar claim `source_ids` and inline `[cite:]` IDs to resolve to Sources. Cross-AKB link Section IDs retain the Section type even when they cannot be resolved offline.
- Copy a truthful RFC 3339 `captured_at` from each non-redacted source's successful persisted capture; never substitute discovery, attempt, or build time.
- Use supported Nurok source types: `feed`, `file`, `firsthand`, `redacted`, or `url`.
- Use `feed` plus `discovered_via_id` when a feed or listing discovered content.
- Deduplicate by the source natural key, normally source type plus canonical URI.
- Keep relative local URIs canonical, rooted inside the working copy, and safe through symlinks.
- Reject absolute paths, parent traversal, and symlinks that resolve outside the working-copy root.

Keep payload stamps aligned with the bytes they describe:

- Source `content_hash` and `content_length` describe the captured evidence bytes, including bytes at `capture_uri` when present.
- Section `content_hash` and `content_length` describe section content bytes.
- Section `provenance_hash` and `provenance_length` describe provenance-sidecar bytes.
- Top-level `guide_hash` and `guide_length` describe guide bytes.
- Do not invent `capture_length`; OpenAKB uses Source `content_length` for captured bytes.

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

Then run the project generator and focused tests and rebuild once to check stability. Treat the current OpenAKB validator and Nurok CLI as authoritative for full descriptor, content, sidecar, inline-citation, policy, path, and deployment-cap validation. Discover the installed validation surface before invoking it:

```bash
nurok --version
nurok kb --help
nurok kb validate --help
```

Use only currently supported arguments. For a verified existing KB, select the explicit remote target through the current CLI so record-dependent checks cannot bind to another KB. Interpret success through the installed command's documented output and require no error-severity issues. Never bypass validation to evade descriptor, content, policy, path, or cap failures.
