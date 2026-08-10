# Original Content And Source-Preserving Sections

Read this reference before accepting Sources, creating or restructuring Sections, or formatting Section content.

## Separate The Units

- **Discovery material**: reposts, translations, search results, and corroborating material used before source approval.
- **Approved Source**: one explicitly selected canonical original document.
- **Capture**: immutable evidence bytes retained from that approved Source.
- **Article body**: the target article's title and authored content after structurally identified page chrome is excluded.
- **Source block**: one independent, ordered representation of an approved Source's article body inside a Section.
- **Section**: one retrieval unit containing one or more independent Source blocks.

Keep discovery material outside the Source registry, Descriptor, Section citations, and source pointers. Do not turn analysis inputs or conclusions into KB content.

## Approve Canonical Originals

Confirm the source boundary before construction:

```text
source | canonical URI | approved original? | capture | intended document boundary
```

Accept a Source only when the user explicitly selected it for the KB, its canonical identity is verified, and a real capture exists. Do not infer approval from the fact that a source was consulted during discovery or verification.

A repost, translation, search result, index, feed, or corroborating document remains excluded when it only helped locate or validate another original. If the user explicitly adds it as a separate in-scope document, require its own canonical identity and capture; never use that approval to authorize cross-source synthesis.

## Principle 1: Preserve Original Content

Keep the complete raw capture immutable. For every article-body range retained in a Source block, preserve every visible word, punctuation mark, capitalization choice, link target, paragraph boundary, and ordering.

Do not correct typos, rewrite headings, join or split sentences, translate, summarize, paraphrase, deduplicate article prose, reorder passages, or insert transitions, explanations, comparisons, and conclusions. Original-only governs the retained text; it does not require page chrome to be copied into Section content.

## Principle 2: Keep Only The Article Body

Select the target article title once and all article prose in original order. Retain original headings, lists, quotations, tables, code, meaningful captions, footnotes, references, and disclosures.

Exclude these elements from Source blocks when structural evidence identifies them as outside the article body:

- global navigation, breadcrumbs, footers, product menus, and cookie or login controls;
- share widgets, newsletter and subscription prompts, and promotional inserts;
- related posts, recommendation cards, `More from the blog`, and CTA labels such as `Read more`, `Try for free`, or `View pricing`;
- repeated title, author, date, category, issue, and reading-time UI from cards or page chrome;
- interaction labels such as `Button` or `Summarize`;
- duplicated scrape blocks and broken labels such as an empty `min read`.

Use DOM containers, stable site templates, repeated UI patterns, or explicit capture ranges as evidence for each exclusion. Do not exclude text merely because it appears unimportant or irrelevant to a planned answer. Keep an ambiguous block or hold the Source for review. Exclusion changes only the Section representation; never delete or alter the immutable capture.

## Build Independent Source Blocks

A Section may cite one or more approved Sources. For every Section:

- list every represented Source exactly once in `source_ids`;
- keep each Source's article body in a separate block;
- map each block to exactly one Source and its ordered included and excluded capture ranges;
- use the Source's own title and headings, preserving stable Section IDs when mappings remain stable;
- preserve order within each Source block;
- never interleave passages or add generated transitions, comparisons, or synthesis across blocks.

One Source may support multiple Sections when length or original structure makes splitting useful. Split only at existing paragraph or heading boundaries and record the ranges assigned to each Section.

## Principle 3: Format For Presentation Only

Use presentation-only Markdown to make the original easier to read. Allowed changes are limited to:

- adding blank lines between paragraphs that already exist in the source;
- rendering an existing source title or heading with Markdown heading markers or bold markers;
- representing existing lists, quotations, tables, links, and code with equivalent Markdown structure;
- separating independent Source blocks without adding visible explanatory prose.

Formatting markers are not source text. When formatting prevents byte equality, keep a Source-block range map or equivalent provenance record that proves the visible text is the same ordered content as the included article-body ranges. Stop when that correspondence cannot be established.

## Define The Local Convention

Write the KB-specific contract in `AKB.md` using `assets/AKB.template.md`. Record:

- the explicitly approved canonical originals and excluded discovery material;
- each Source-block-to-Section mapping and block order;
- the included article-body ranges, structurally excluded page-chrome ranges, and evidence for exclusions;
- the permitted presentation-only formatting;
- the provenance method used to compare Section text with capture ranges;
- the checks required before create, update, and push.

Update `AKB.md` before the generator whenever approved Sources, article-body boundaries, Source-block mappings, Section ranges, or formatting rules change.

## Verify Every Build

For every build, review Source approval, capture availability, complete `source_ids`, Source-block boundaries, included and excluded capture ranges, block order, duplicate canonical URIs, provenance gaps, and content differences. Compare each block's visible text with its included article-body ranges. Treat any unexplained addition, omission from the article body, replacement, reorder, interleaving, or page-chrome exclusion without structural evidence as a blocking error.
