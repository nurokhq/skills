# Nurok Submission Record

This is a preparation record, not an attestation of public-directory readiness. Source and GitHub artifacts can be reviewed while the remaining service, publisher, and device checks are completed.

## Listing And Publisher

The package includes the Nurok identity, read-only description, three starter prompts, real logo/composer icon, remote MCP endpoint, and five positive plus three negative review cases. It reuses the existing Nurok author metadata; the verified developer identity in the submission portal must still be selected by the publisher.

The linked Nurok privacy and terms pages cover the service and related APIs, but both currently identify themselves as first-pass drafts pending final legal review. Their URLs are real and public; the publisher must confirm they are finalized and cover this plugin's actual processing before submission. See [privacy](https://nurok.ai/legal/privacy) and [terms](https://nurok.ai/legal/terms).

Country availability and commerce declarations remain unspecified pending publisher input. Do not infer either from the website's subscription language. Reviewer credentials, if required for future private-access cases, belong only in secure portal fields.

## Live Read Checks — 2026-10-08

These checks exercised the production MCP through the existing Codex connection and, for protocol discovery, anonymous HTTPS requests. They did not install the newly generated package on mobile, Mac, or Windows.

| Check | Status | Evidence |
| --- | --- | --- |
| Anonymous protocol initialization | Passed | Standard HTTP client received HTTP 200, protocol `2025-03-26`, server `nurok-mcp` version `0.1.0`. |
| Anonymous tool discovery | Passed | `tools/list` returned 13 read tools; no write tools. |
| Public tags and bounded catalog | Passed | Public tag page and two public catalog entries returned without mutation. |
| KB resolution | Passed | `yellow/alchemist-flagship` resolved to `01a07f25-d5ca-76b3-beb5-46eded2f73e8`, public, live revision `r4`. |
| Pinned structure | Passed | Depth-1 listing at `r4` returned two top-level sections and `resolved_revision: r4`. |
| Search and full Section retrieval | Passed | Query `application` returned `SEC-AB2D6A`; full retrieval returned 16,991 bytes at the selected revision. |
| Provenance retrieval | Passed | `kb_artifact` returned the Section's provenance at `r4`, linking `SRC-000013` to its full Section byte range. |
| Source visibility | Passed at tool level | The Section's Source is explicitly private; its URL must remain hidden even though the KB is public. No identifying Source metadata is copied here. |
| Revision history | Passed | Bounded changelog returned revisions `r4` and `r3` with a continuation cursor. |
| Natural-language review cases in the installed release | Not run | Tool-level smoke checks do not prove skill activation, routing, or negative-case behavior. |
| ChatGPT iOS/Android, macOS, Windows installation | Not run | Requires the actual installed release and supported accounts/clients. |
| Private-account OAuth connection | Not run | The package declares `mixed` auth with the provided public client `nurok-chatgpt-prod`. Portal connection, sign-in, token exchange, and authorized tool calls have not been verified. |

The public fixture can evolve or disappear. Resolve it before each run, pin the returned revision, and report missing fixture access rather than inventing successful results. Negative cases remain unrun until exercised in the installed plugin.

## Server Review Gaps

The live 13 tools all declare `readOnlyHint: true`. Their `annotations` currently omit `destructiveHint` and `openWorldHint`, and they expose no per-tool `securitySchemes`. Before public review, the MCP service owner must:

- Preserve `readOnlyHint: true` and explicitly declare `destructiveHint: false`; no write functionality is needed. MCP itself makes these hints optional, but the OpenAI plugin review requires explicit annotations.
- Declare `openWorldHint` per tool: `false` for reads confined to the managed Nurok knowledge corpus, `true` if the tool accesses arbitrary external entities or fetches arbitrary internet URLs. A remote endpoint or public KB does not by itself establish open-world behavior. Confirm the server implementation before selecting the value.
- Declare per-tool `securitySchemes` (`noauth` plus `oauth2` with `kb:read`) and return a `_meta["mcp/www_authenticate"]` challenge when an anonymous call needs sign-in. ChatGPT shows account linking only with both. Verify the connection flow; do not imply private OAuth access from a working anonymous read.
- Re-scan the actual deployed server and address portal findings. Editing `mcp.json` cannot repair server-owned tool metadata.

These are descriptive hints, not permission grants or access controls. In MCP, `destructiveHint` is meaningful only for tools that are not read-only. See the [MCP annotation definitions](https://kotlin.sdk.modelcontextprotocol.io/kotlin-sdk-core/io.modelcontextprotocol.kotlin.sdk.types/-tool-annotations/index.html) and [OpenAI plugin reference](https://developers.openai.com/plugins/reference).

No server source is modified by this repository change.

## OAuth Client

The package uses `mixed` authentication with a preregistered public client instead of Dynamic Client Registration:

| Setting | Value |
| --- | --- |
| Client mode | `provided` |
| Client ID | `nurok-chatgpt-prod` |
| Token endpoint auth method | `none` |
| Base scopes | `kb:read` |

Before connecting, register this client in the Nurok authorization server with the exact callback URI shown by the portal connection flow.

After uploading a new version, inspect the saved MCP settings before selecting **Connect**. They must show the provided client and no client-secret field. Uploading a ZIP may not replace a connection's earlier registration settings.

## Device Acceptance And Demo

Run the installed package on each target: ChatGPT iOS, Android, macOS, Windows, and supported Codex. Record client version, account/workspace eligibility, package version, and pass/fail evidence. Use the same public fixture and prompts on each device.

1. Find and install Nurok, complete the remote connection flow if requested, and start a new conversation.
2. Browse two public KBs and resolve the fixture without installing CLI/Python or connecting a personal computer.
3. Browse the fixture, ask an application question, and verify its pinned evidence and private Source redaction.
4. Inspect revision history and test an unavailable or unauthorized KB without fabricated results.
5. Run the three negative cases: deletion, capture/publication, and local-folder upload must not invoke writes or local commands.

For the required demo recording, capture real interactions in a supported host: show the installed Nurok release, catalog prompt, resolved fixture, an evidence-backed answer, and a rejected write request. Hide personal account details and credentials. A device screen recorder can record this sequence; review the saved video, host it at a reviewer-accessible URL, and add the verified URL as `extensions.com.openai.review.demo_recording_url`. This walkthrough is a recording plan, not a completed recording.

Before submission, complete publisher verification, country/commerce declarations, domain verification, finalized policy coverage, server annotations/auth checks, the recording URL, actual review-case execution, and portal scans. Approval and publication remain separate actions after those checks.
