# Preserve Original Content In Sections

Read this reference before accepting Sources, selecting evidence, creating or restructuring Sections, assigning titles, or formatting Section content.

## Separate The Units

- **Discovery material**: reposts, translations, search results, and corroborating material consulted before Source approval.
- **Approved Source**: one canonical original covered by explicit approval or an approved objective inclusion rule.
- **Capture**: immutable evidence retained from one approved Source.
- **Article body**: the Source's authored title and content after structurally identified page chrome is excluded.
- **Source block**: one independent, ordered representation of exact evidence from one Source inside a Section.
- **Section**: one retrieval unit containing one or more independent Source blocks under an approved Section-class responsibility.

Keep discovery material outside the Source registry, Descriptor, Section citations, and source pointers. Never turn analysis inputs or conclusions into KB content.

## Approve Canonical Sources

Accept a Source only when its canonical identity is verified, real immutable evidence exists, and either the user explicitly selected it for the KB or it objectively satisfies the approved scope inclusion rule.

A repost, translation, search result, index, feed, or corroborating document remains excluded when it only helped locate or validate another original. If it is separately approved as its own canonical Source, require its own identity and capture. Source approval never authorizes cross-Source synthesis.

## Follow The Approved Section Class

Use the mapping and evidence policy approved in `.nurok/structure.md` for the Section's class. Supported outcomes include, but are not limited to:

- one whole Source represented in one Section;
- one long Source split into ordered Sections at original structural boundaries;
- one Source supporting multiple retrieval responsibilities through separately traced excerpts; and
- one Section containing exact evidence from multiple visibly separate Sources.

Do not apply one Section class's selection rule to another. A document-preserving class may require the complete article body and original context. An evidence-focused class may select only exact ranges directly relevant to its approved responsibility. Selection may omit irrelevant article-body ranges only when the class permits excerpting; it must never alter the selected text or misrepresent the omitted context.

Keep the complete capture immutable regardless of how much appears in a Section.

## Select Exact Source Evidence

For every selected range, preserve each visible word, punctuation mark, capitalization choice, link target, paragraph boundary, and original ordering. Select at complete paragraphs, original headings, or another provable boundary.

Never correct typos, rewrite headings, join or split sentences, translate, summarize, paraphrase, deduplicate Source prose, reorder passages, or insert transitions, explanations, comparisons, and conclusions.

Exclude navigation, breadcrumbs, footers, product menus, controls, widgets, subscription prompts, promotional inserts, related-content cards, repeated UI metadata, duplicated scrape blocks, and broken UI labels only when DOM containers, stable site templates, repeated UI patterns, or explicit capture ranges prove they are outside the article body. Never exclude text merely because it seems unimportant. Keep ambiguous material or hold the Source for direction.

## Build Independent Source Blocks

Start every Source block in this order:

```markdown
<!-- source-block:<Source ID> -->
[cite:<Source ID>]

## <Source identity label>
```

Use this deterministic visible label priority:

1. a Source title verifiable from the capture;
2. the canonical Source URL when no reliable original title exists; or
3. the stable Source ID when the URL is unavailable or unsuitable for display.

The Source label only distinguishes blocks. It is not a generated summary, interpretation, or claim about the Source.

For every Section:

- list every represented Source exactly once in Descriptor `source_ids` and in block order;
- keep each Source in its own visible block;
- map each block to exactly one Source and its ordered selected and excluded ranges;
- preserve original order within each block;
- place a clear Markdown separation before the next Source block; and
- never interleave blocks or add generated transitions, comparisons, explanations, consensus, or synthesis.

When one block contains multiple noncontiguous excerpts from the same Source:

- keep them in original order;
- select complete paragraphs or other provable boundaries;
- separate them visibly without generated explanatory transitions;
- record every exact range separately; and
- never claim one continuous range that covers omitted content.

The provenance method may vary by project, but it must map each exact range to the block deterministically. Do not change the OpenAKB audit or invent a universal range schema for this purpose.

## Assign Section Titles And Metadata

Make every content Section title a direct, verifiable summary of all Source blocks visible in that Section. A Section title is distinct from each Source-block identity label.

Use only visible selected evidence. Do not use hidden capture content, external information, Agent knowledge, or an inferred relationship among Sources. Do not add facts, causality, evaluation, certainty, or false consensus. When the visible evidence does not support a specific title, use a more neutral topic summary.

A parent or category without content may use a user-approved navigation label or purpose description. It may describe organization, but must not state unsupported domain facts.

Apply the same boundary to Descriptor and `AKB.md` titles, descriptions, summaries, prompts, and tags. They may express the approved topic, audience, use, scope, and retrieval entry points, but must not become a path for unsourced facts, synthesis, or marketing claims.

## Format For Presentation Only

Allowed presentation changes are limited to:

- adding blank lines between paragraphs that already exist;
- rendering an existing Source title or heading with Markdown heading or bold markers;
- representing existing lists, quotations, tables, links, and code with equivalent Markdown structure; and
- visually separating independent blocks or noncontiguous excerpts without adding explanatory prose.

Formatting markers are not Source text. When formatting prevents byte equality, keep a Source-block range map or equivalent provenance record proving that visible text is the same ordered content as the selected ranges. Stop when that correspondence cannot be established.

## Verify Every Build

Review Source approval, capture availability, Section-class responsibility, complete `source_ids`, Source-block boundaries, exact selected and excluded ranges, block order, duplicate canonical URIs, title support, provenance gaps, and content differences.

Compare each block's visible Source text with its selected ranges. Treat any unexplained addition, omission required by the class policy, replacement, reorder, interleaving, unsupported page-chrome exclusion, inferred Section title, or cross-Source synthesis as blocking.
