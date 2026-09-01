# Build Or Repair A Working Copy

Read this reference when creating `openakb.json`, repairing KB artifacts, or changing metadata, sections, sources, content, or generation logic.

For a new KB or structural redesign, first read [scope-and-structure.md](scope-and-structure.md) and require the applicable approved contracts. Keep all KB-creation process artifacts in `.nurok`; keep formal OpenAKB artifacts in Descriptor-projected locations.

## Scaffold A New Working Copy

For a new KB, inspect the installed CLI and use its supported offline scaffold instead of recreating the base descriptor by hand:

```bash
nurok --version
nurok kb --help
nurok kb init --help
```

Use only options shown by the installed help. Run the scaffold only for an authorized new local destination after the user has approved the concrete scope, structure rules, and representative structure sample. Inspect overwrite behavior before execution and do not work around protections. Project the approved contracts into `assets/AKB.template.md`, then update the Descriptor and content through the declared source of truth.

## Define Audience Metadata

Use a literal subject-specific KB title. Write a concise description expressing the approved topic, audience, use, corpus boundary, and provenance without adding claims about Source content. Keep the Nurok summary aligned unless the user requests different copy:

```json
{
  "title": "<Subject> Knowledge Base",
  "description": "<Approved topic, audience, use, corpus boundary, and provenance>",
  "x": {
    "ai.nurok": {
      "summary": "<Same value as description>"
    }
  }
}
```

Omit suggested prompts unless the user supplies them. When prompts are required, use literal retrieval prompts about a named original document; do not analyze the document to generate synthesis, comparison, or interpretive prompts.

## Build The Descriptor

- Use `$schema: https://schema.openakb.org/v1/openakb.schema.json`.
- Keep top-level Descriptor `id` and `namespace` as `[a-z0-9_-]` slugs of at most 64 characters.
- Give every Source an ID matching `SRC-[0-9A-Za-z]{6}` and every Section an ID matching `SEC-[0-9A-Za-z]{6}`. Compare IDs case-insensitively in one shared identity space. Prefer uppercase prefixes with lowercase bodies when minting IDs.
- Preserve an existing `namespace`; it binds the working copy to its remote owner.
- Declare only explicitly approved canonical original Sources with real immutable captures. Keep discovery and auxiliary material outside the Descriptor.
- Give every category and Section a non-empty description supported by the approved purpose or visible Source evidence.
- Omit `parent_id` from root categories. Require every `parent_id` to resolve to a Section and keep the parent graph acyclic.
- Give every section with `content_uri` one or more `source_ids` citations. Require each ID to be unique case-insensitively and resolve to a declared Source. List every Source represented by an independent Source block and no others.
- Start every independent Source block with `<!-- source-block:<Source ID> -->` followed by `[cite:<Source ID>]`. Keep Source block markers, inline citations, Descriptor `source_ids`, provenance `source_ids`, and provenance `source_blocks[].source_id` in the same order.
- After the marker and citation, use a verifiable original Source title as the first visible identity label, then the canonical Source URL, then the stable Source ID. Use the label only to distinguish the block; do not generate a block summary.
- Make every content Section title a direct, verifiable summary of all Source blocks visible in that Section. Do not use hidden capture content or inferred relationships.
- Use `sections/<section-id>/content.md` for hosted Markdown content.
- Treat `content_type` as optional with the OpenAKB default `text/markdown`; do not make it mandatory because of a CLI or consumer implementation.
- Require `discovered_via_id` to resolve to a Source. Require local link `section_id` and provenance-sidecar `section_id` to resolve to a Section; require sidecar claim `source_ids` and inline `[cite:]` IDs to resolve to Sources. Cross-AKB link Section IDs retain the Section type even when they cannot be resolved offline.
- Copy a truthful RFC 3339 `captured_at` from each non-redacted source's successful persisted capture; never substitute discovery, attempt, or build time.
- Use supported Nurok source types: `feed`, `file`, `firsthand`, `redacted`, or `url`.
- Use a feed, listing, or `discovered_via_id` only when that document is itself an explicitly approved canonical original in scope, not merely discovery material.
- Deduplicate by the source natural key, normally source type plus canonical URI.
- Keep relative local URIs canonical, rooted inside the working copy, and safe through symlinks.
- Reject absolute paths, parent traversal, and symlinks that resolve outside the working-copy root.
- Never reference `.nurok` from the Descriptor or include it directly in a publishing copy. Publish only the validated Descriptor projection of formal artifacts.

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

Prefer public pointer visibility for a Source of type `url` when its canonical URL and identifying metadata are already public and safe to disclose. Treat this as a recommendation, not as authority to mutate a remote Source registry. Do not infer KB record visibility from Source visibility.

For every private Source, keep provenance artifacts non-identifying. Refer to the Source only by its opaque stable Source ID and preserve the Section, block, range, and order mapping required for deterministic traceability. Never copy its canonical or capture URL, title, provider or owner name, filename or path, visible Source-block label, or any other source-identifying information into provenance. A private KB does not relax this rule.

## Select And Format Section Content

Apply these rules in order whenever creating a Section `content.md`:

1. Keep the immutable capture complete and unchanged.
2. Resolve the Section's approved class, stable retrieval responsibility, Source mapping, content-selection rule, and evidence policy.
3. Identify eligible article-body ranges through original structure, DOM evidence, stable site templates, repeated UI patterns, or explicit capture ranges.
4. Select the complete article body when the class requires document preservation, or exact relevant ranges when the class permits excerpting. Use complete paragraphs or other provable boundaries and keep original order.
5. Exclude only structurally identified page chrome. Keep or hold ambiguous material for direction.
6. Start each Source block with its marker, matching citation, and Source identity label. Preserve every selected word, punctuation mark, capitalization choice, link target, paragraph boundary, and ordering.
7. Assign a Section title that directly summarizes all visible Source blocks without inference or unsupported consensus.
8. Apply presentation-only Markdown around existing Source structure. Never correct, translate, summarize Source prose, paraphrase, deduplicate, reorder, or add explanatory text.
9. Immediately after generating or regenerating the file, run the KB project's configured Markdown formatting or lint tool against it. Fix every formatting error and rerun the same tool until it passes. If the tool is absent, stop; do not substitute an unrelated check or let an automatic fix change Source text.

When a Section represents multiple Sources, keep each Source in an independent block. Do not interleave or merge prose and do not add transitions, comparison, or synthesis. Ensure `source_ids` lists every represented Source.

Record every block's exact ordered selected ranges separately, plus excluded page-chrome ranges and structural evidence or equivalent provenance. Never use one covering range for noncontiguous excerpts. After the Markdown tool passes, compare the block's visible Source text with its selected ranges and stop on any unexplained difference or exclusion.

## Keep Generation Deterministic

Change the generator or declared source of truth rather than only editing generated JSON. Keep immutable captures separate from presentation-formatted Section files.

- Reuse capture timestamps for unchanged sources.
- Preserve stable Source and Section IDs across rebuilds. Apply each Section class's approved stable-identity rule; do not use a changing byte range as the sole identity.
- Define metadata, Section-class mappings, evidence selection, Source-block structure, Section-title rules, presentation rules, and pointer extensions once in the generator.
- Preserve `guide_hash`, `guide_length`, `content_hash`, `content_length`, and provenance stamps when bytes are unchanged.
- Compare aggregate content hashes before and after regeneration.
- Regenerate `AKB.md` from the current approved `.nurok` contracts and regenerate `sections/` only when their inputs or declared convention changed. Stop on control-plane, guide, or Descriptor conflict.

Add focused tests for exact metadata, complete `source_ids`, independent Source blocks, Section-class selection rules, exact selected and excluded range correspondence, supported summary titles, presentation-only formatting, pointer declarations, stable namespace, stable timestamps, stable knowledge-unit IDs, deterministic output, and project-specific counts or deduplication invariants.

## Audit And Validate

Before the structural audit, compare every Source block's visible text and order with its included article-body ranges. Confirm that every excluded range is page chrome supported by structural evidence. Treat any unexplained content difference, exclusion, interleaving, or provenance gap as an error. Then run the bundled supplemental audit:

```bash
python3 <skill-dir>/scripts/audit_working_copy.py --dir <working-copy>
```

The audit recomputes every present local blob's SHA-256 and byte length, checks ordered Source-block and citation relationships, validates declared provenance identities and ranges, and reports an aggregate digest over `openakb.json` plus every Descriptor-referenced local blob. Use `--format json` when a generator, CI job, or creation log consumes the result.

Fix every error and review every warning. Exit status `0` means no audit errors, `1` means blocking findings, and `2` means the audit could not run. A stamps-only warning is valid only when the target or base snapshot already has that blob; restore the local file before creating a new KB or whenever blob availability is uncertain.

Then run the project generator and focused tests and rebuild once to check stability. Treat the current OpenAKB validator and Nurok CLI as authoritative for full descriptor, content, sidecar, inline-citation, policy, path, and deployment-cap validation. Discover the installed validation surface before invoking it:

```bash
nurok --version
nurok kb --help
nurok kb validate --help
```

Use only currently supported arguments. For a verified existing KB, select the explicit remote target through the current CLI so record-dependent checks cannot bind to another KB. Interpret success through the installed command's documented output and require no error-severity issues. Never bypass validation to evade descriptor, content, policy, path, or cap failures.
