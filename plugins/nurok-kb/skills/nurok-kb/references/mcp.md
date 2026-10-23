# Nurok MCP Read Workflow

Use this workflow after selecting MCP in `SKILL.md`. Inspect the runtime tool descriptions and schemas before each workflow; host namespaces and fields may differ. Do not hardcode a tool namespace or reuse arguments from another deployment.

## Confirm The Read Surface

Allow only these semantic MCP operations when the runtime exposes them:

- `kb_tags_list`
- `kb_list`
- `kb_discover`
- `kb_resolve`
- `kb_get`
- `kb_changelog`
- `kb_sections_list`
- `kb_section_get`
- `kb_subtree_read`
- `kb_search`
- `kb_sources_list`
- `kb_source_get`
- `kb_artifact`
- MCP resource reads for exact resource URIs returned by those operations

Call no other Nurok MCP operation. This remote workflow requires no shell, local files, CLI installation, or locally stored credentials. Use the host's supported connection flow if tools are unavailable; do not replace a failed connection with invented knowledge.

Record the public API and web bases reported by the server without exposing authentication material. Anonymous reads may cover public KBs; private access depends on the current viewer and supported server authentication. A local CLI login does not establish the MCP viewer's identity. Preserve authorization failures and never retry them against another account or endpoint without authority.

## Choose The KB

Prefer an identity supplied by the user or established in the conversation:

1. For `{owner_handle}/{slug}`, or that visible path under the server's configured web base when supported by its current contract, call `kb_resolve` and use its returned canonical `kb_id` for every later read.
2. For a canonical KB UUID, call `kb_get` and keep that UUID for subsequent reads.
3. Accept an absolute KB API URL only when it uses the server's configured public API base and its visible relative path is either `/v1/kbs/{kb_id}` or `/v1/kbs/resolve/{owner_handle}/{slug}`. Allow only a trailing slash or a deeper revision or artifact path after a grammar-valid KB UUID. Do not treat query strings, fragments, percent-encoded text, malformed segments, or opaque IDs as new identity components.

For a topical question without a KB identity, use `kb_discover` when available. Distill the topic into a focused query using the runtime's documented language guidance. Add filters only when supplied or confirmed; never invent exact tags. Its score ranks one response and is not a calibrated confidence threshold. Proceed on one clear match, otherwise ask the user to choose a returned identity.

When discovery is unavailable, inspect one bounded `kb_tags_list` page or confirm a plausible tag substring with `q`, then use an exact confirmed tag with `kb_list`. An empty tag match is inconclusive. Do not select a topical KB from an unfiltered catalog or from popularity. Unfiltered `kb_list` is reserved for explicit catalog requests, with bounded cursor pagination.

## Browse And Retrieve

Use the canonical `kb_id` and selected revision from the identity lookup. Preserve `resolved_revision` returned by pinned reads. Keep identity, revision, query, and filters unchanged while following a cursor; disclose partial coverage.

For a topical or factual question, use `kb_search` with a focused query. Treat hits as discovery evidence and retrieve every material Section with `kb_section_get` before citing it. If the runtime reports a pending index, label the result provisional; a bounded retry may help. Do not interpret an empty result as proof that the KB contains no relevant evidence.

For structure or an exhaustive survey, use `kb_sections_list` as the table of contents. Start with depth 1 or 2, inspect titles and descriptions, and recurse with `parent_id` as needed. When supported, use `kb_subtree_read` to retrieve a selected branch in descriptor order. Search results alone do not establish exhaustive coverage.

Use available metadata, excerpt, and full-content modes according to the task. An excerpt is a literal slice, not the complete Section. When a tool returns inline content, use it. When `omitted_fields` indicates missing content and an exact `content_uri` is returned, read that resource if the host supports it. Otherwise use `kb_artifact` according to its current schema, using the verified Section ID and documented offset or length fields for bounded reads. Never invent a resource URI, artifact path, offset, or argument. Resource fallback must work without local filesystem access.

Use `kb_artifact` for a structured Descriptor or one published raw artifact at the selected revision. Use `kb_sources_list` and `kb_source_get` only when needed to resolve a Source used by the answer. Prefer the returned `web_url` for KB navigation and returned public Source URIs for factual citations. Respect explicit private Source markers even inside a public KB.

For answers or syntheses that make material claims, complete [the provenance workflow](provenance.md) for every Section used. Keep the KB and revision pinned across Section, provenance, and Source reads; report missing evidence instead of inventing citations.

## Read Descriptor And Provenance Artifacts

For `kb_artifact`, the structured Descriptor uses `kind: "openakb"`; `descriptor` is a response field, not an accepted `kind`. Section provenance uses `kind: "provenance"` with `section_id`. Replace the placeholders below with the canonical KB ID, pinned revision, and Section ID returned by earlier reads.

Descriptor, when needed to resolve metadata or Source visibility:

```json
{"kb_id":"<resolved-kb-id>","revision":"<pinned-revision>","kind":"openakb"}
```

Provenance for a retrieved Section:

```json
{"kb_id":"<resolved-kb-id>","revision":"<pinned-revision>","kind":"provenance","section_id":"<returned-section-id>"}
```

Read Section provenance directly when its identity is known; fetching the Descriptor first is not required to read provenance. Read the returned inline artifact or exact resource URI before classifying evidence. Before disclosing any Source identity from that provenance, read the Descriptor at the same revision, or use verified returned Source-registry state, to resolve Source visibility as [the provenance workflow](provenance.md) requires. If visibility cannot be resolved, disclose only the opaque Source ID and mark the evidence incomplete.

When the runtime exposes the `kb_artifact` input schema, follow it; it overrides these examples. Use these argument shapes only when the host renders the schema as `unknown` or hides its fields. On `validation.failed`, compare the rejected arguments with the schema and these examples, correct a confirmed mismatch, and retry once at the same KB and revision. A parameter-validation error alone does not establish missing provenance or failed authorization. If the corrected read still fails, report the actual error and mark the evidence incomplete.
