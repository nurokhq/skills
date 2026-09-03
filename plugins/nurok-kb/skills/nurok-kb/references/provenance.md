# Show Answer Provenance

Use this workflow for answers, comparisons, and syntheses that make material claims from KB content. Do not add Source-level provenance to simple KB discovery, metadata, search-candidate, or changelog output unless that output supports a knowledge claim.

## Build The Evidence Chain

Pin all reads that support one answer to the same canonical KB and revision. For every material Section used in the answer:

1. Retrieve the Section content rather than relying on a search hit.
2. Resolve the Section's returned or Descriptor-declared `provenance_uri` without inventing a path, and read that provenance artifact at the pinned revision.
3. Resolve every material `source_id` to its published Source metadata. Treat a Source as public unless the retrieved Descriptor or verified returned Source-registry state explicitly marks it private; any explicit private marker wins. Never infer Source visibility from KB record visibility. Preserve a public Source's returned ID, type, URI, capture timestamp, and capture metadata. Key an explicitly private Source only by its opaque stable Source ID and non-identifying Section, block, range, and order mapping. If the required metadata cannot be resolved, record the missing link and classify the evidence as incomplete.
4. Record the answer claim, KB, revision, Section, provenance entry, and Source as one evidence chain.

With the CLI, use `nurok kb section get` for the Section and cited Source metadata. Use `nurok kb cat` at the same revision to read `openakb.json` or one returned provenance artifact when required. Owner Source-registry commands remain outside this skill's read boundary.

With MCP, use `kb_section_get` and exact returned resource URIs for content. Use `kb_artifact` according to its current schema for the Descriptor or provenance artifact, and use `kb_sources_list` or `kb_source_get` when needed to resolve a Source used by the answer. Read [the MCP workflow](mcp.md) for the complete MCP boundary.

Do not read a raw capture merely to populate the compact provenance display. Read one only when the user requests evidence verification or when resolving a material conflict requires it, and only through an allowed read operation at the same revision.

## Classify Evidence Granularity

Assign the finest level actually established by the retrieved artifacts:

- `claim`: a provenance `claims` entry directly supports the answer claim and identifies its Source IDs.
- `source-block`: provenance maps a supporting Source block to a non-empty Section byte range, but no direct claim mapping is available.
- `section`: the Section identifies supporting Source IDs, but no usable claim or Source-block mapping is available.
- `incomplete`: required provenance is missing, inaccessible, stale, or conflicting.

Do not describe Section-level or Source-block-level evidence as claim-level support. A hash proves byte identity, not truth, authority, or semantic support.

## Preserve Answer Integrity

Label live metadata separately from revision-pinned content. Distinguish quotation and paraphrase from synthesis or inference, and disclose sampled or otherwise limited coverage. Preserve returned identities and disclosed URIs exactly. Never invent citations, identifiers, Source URLs, capture metadata, or evidence precision.

## Present Compact Provenance

Place compact markers such as `[P1]` immediately after each material claim or tightly related claim group. Reuse a marker only when the claims have the same evidence chain. One marker may name multiple Sources when they jointly support the claim.

Add a `Provenance` section after the answer. For each marker, show by default:

- canonical KB identity and pinned revision;
- Section ID or published artifact path;
- every supporting Source ID;
- evidence granularity.

For every public Source, also show its original URI. For every explicitly private Source, show no URL, title, provider or owner name, filename or path, visible label, or other source-identifying information. Expanded provenance for an explicitly private Source may add only the non-identifying Section, block, range, and order mapping required for deterministic traceability.

When the user directly requests identifying metadata for an explicitly private Source, state briefly that the Source is private and omit the requested metadata.

For public Sources, show capture timestamps, capture URIs, hashes, provenance artifact paths, and byte ranges only when the user requests expanded provenance or when they are necessary to explain a conflict or limitation. Preserve public non-HTTP Source identities and already-redacted identifiers as returned; do not manufacture public links.

For example:

```markdown
The material claim appears here. [P1]

## Provenance

- [P1] `owner/kb@revision`
  - Section: `SEC-000001`
  - Source: `SRC-000001` — `https://example.com/source`
  - Evidence: `source-block`
- [P2] `owner/kb@revision`
  - Section: `SEC-000002`
  - Source: `SRC-000002` (private)
  - Evidence: `source-block`
```

## Degrade Explicitly

When a material claim has incomplete provenance, label it `incomplete`, state which link in the evidence chain is missing or conflicting, and keep it separate from fully traced claims. The answer may still include it unless the user requests only fully traced evidence.

When the user requests only fully traced evidence, omit incompletely traced claims and report the resulting coverage gap. Never silently substitute a live revision, another KB, an unpinned Source, or a weaker evidence level.
