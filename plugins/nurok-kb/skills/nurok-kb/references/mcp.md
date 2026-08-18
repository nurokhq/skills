# Nurok MCP Read Workflow

Use this workflow after selecting MCP in `SKILL.md`. Inspect the runtime tool descriptions and schemas before each workflow; host namespaces and fields may differ. Do not hardcode a tool namespace or reuse arguments from another deployment.

## Confirm The Read Surface

Allow only these semantic MCP operations when the runtime exposes them:

- `kb_tags_list`
- `kb_list`
- `kb_resolve`
- `kb_get`
- `kb_changelog`
- `kb_sections_list`
- `kb_section_get`
- `kb_search`
- `kb_sources_list`
- `kb_source_get`
- `kb_artifact`
- MCP resource reads for exact resource URIs returned by those operations

Call no other Nurok MCP operation.

Record the public API base reported by the server without exposing authentication material. Anonymous reads may cover public KBs; private access depends on the current viewer and server authentication.

## Choose The KB

Prefer an identity supplied by the user or established in the conversation:

1. For `{owner_handle}/{slug}`, call `kb_resolve` and use its returned canonical `kb_id` for every later read.
2. For a canonical KB UUID, call `kb_get` and keep that UUID for later reads.
3. Accept an absolute KB API URL only when it uses the server's configured public API base and its visible relative path is either `/v1/kbs/{kb_id}` or `/v1/kbs/resolve/{owner_handle}/{slug}`. Allow only a trailing slash or a deeper revision or artifact path after a grammar-valid KB UUID. Do not treat query strings, fragments, percent-encoded text, malformed segments, or opaque IDs as new identity components.

For a topical question without a KB identity:

1. Inspect one bounded `kb_tags_list` page without `q`.
2. Optionally narrow with `q` only for a plausible tag substring; an empty result is inconclusive.
3. If exactly one tag clearly matches, pass its exact spelling to `kb_list` with supported context filters.
4. Otherwise ask for `{owner_handle}/{slug}`, a canonical UUID, or a Nurok KB API URL. Do not select a topical KB from an unfiltered list.

Do not use popularity as semantic relevance or exhaustively page tags or KBs to manufacture a match.

## Browse And Retrieve

Pass the canonical `kb_id` and selected revision from `kb_resolve` or `kb_get` to later reads.

Use `kb_sections_list` as the first broad discovery operation inside the selected KB. For a large KB, start at depth 1 or 2, inspect titles and descriptions as a table of contents, and recurse with `parent_id` only into promising branches. Follow `next_cursor` only when more entries are required for the request.

Use `kb_search` only as a secondary exact-term aid. It may miss multilingual, paraphrased, or incompletely indexed content. Treat search results as discovery evidence and retrieve every material Section with `kb_section_get` before citing it.

When `kb_section_get` returns inline content, use that bounded content. When it returns only a `content_uri`, perform an MCP resource read on that exact URI. If resource reads are unavailable, use `kb_artifact` only according to its current schema and use documented offset or length fields for large content. Never invent a resource URI, artifact path, offset, or argument.

Use `kb_artifact` for a structured Descriptor or one published raw artifact at a live or pinned revision. Read only returned artifact paths or URIs. Use `kb_sources_list` and `kb_source_get` only when retrieved Sections lack required Source metadata.
