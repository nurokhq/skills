# <Knowledge Base Title>

<One-sentence description of the approved canonical original documents preserved by this knowledge base.>

## Scope Contract

This KB preserves <approved canonical original documents> for verbatim retrieval by <audience>, within <explicit boundaries>.

### Approved Canonical Originals

| Source | Canonical URI | Capture | Document Boundary | Approval |
| --- | --- | --- | --- | --- |
| <Original document> | <Canonical URI> | <Hash-pinned capture> | <Whole document or explicit boundary> | <User authorization> |

### Excluded Discovery Material

- <Repost, translation, search result, index, or corroborating source used only to locate or verify an original>

### Explicit Boundaries

- <Included document, source type, time, or language boundary>
- <Excluded material and why it is not an approved original>

## Original Content Policy

- Treat each approved canonical original as one stable document boundary.
- Preserve the immutable capture, canonical URI, publisher or author, capture time, content hash, and content length.
- Keep discovery notes, auxiliary evidence, summaries, translations, analysis, and other derived material outside the KB.
- Keep every immutable capture complete and unchanged.
- Apply original-only to every retained article-body range: preserve every visible source word, punctuation mark, capitalization choice, link target, paragraph boundary, and ordering.
- Apply article-body-only to each Source block: omit only structurally identified page chrome and retain the title once plus all article prose.

## Source Block Structure

| Section | Source Block | Source | Original Title | Included Article-Body Ranges | Excluded Page-Chrome Ranges And Evidence | Order |
| --- | --- | --- | --- | --- | --- | --- |
| <Section ID> | <Stable block ID or index> | <Source ID> | <Exact original text> | <Ranges or equivalent provenance> | <Ranges plus DOM/template/repetition evidence> | <Sequence> |

A Section may contain one or more Sources, and one Source may support several Sections. List every represented Source in the Section's `source_ids`. Keep each Source in an independent block; never interleave prose or add transitions, comparisons, or synthesis across blocks.

## Article-Body Selection

Keep the article title once, all article prose in original order, original headings, lists, quotations, tables, code, and meaningful captions, footnotes, references, and disclosures.

Exclude navigation, breadcrumbs, footers, product menus, cookie or login controls, share widgets, newsletter or subscription prompts, related-post cards, CTA labels, repeated title/byline/date/category/issue/read-time UI, interaction labels, duplicated scrape blocks, and broken UI labels only when structural evidence identifies them as outside the article body. Never exclude text merely because it seems unimportant. Keep or hold ambiguous material for review, and never alter the capture.

## Section Formatting

Allow presentation-only Markdown that makes the original easier to read:

- Add blank lines only between existing source paragraphs.
- Render an existing title or heading with Markdown heading markers or bold markers while copying its visible text exactly.
- Represent existing lists, quotations, tables, links, and code with equivalent Markdown structure.
- Split long documents only at existing paragraph or heading boundaries and retain source order.

Do not correct, rewrite, translate, summarize, paraphrase, deduplicate article prose, join or split sentences, reorder, add transitions, or insert explanations and conclusions.

When formatting prevents byte equality, record Source-block ranges or equivalent provenance that proves the visible text remains the same ordered content as the included article-body ranges.

## Update Protocol

1. Confirm explicit approval and a valid immutable capture for every added Source.
2. Update the Source-block map plus included and excluded ranges without changing unrelated Sources.
3. Confirm that every exclusion is structurally identified page chrome and apply only the presentation formatting allowed above.
4. Compare every Source block's visible text and order with its included article-body ranges.
5. Regenerate deterministically, run focused tests and the bundled audit, and complete OpenAKB validation.
6. Repeat original-content comparison on the publishing copy before push.

## Quality Gates

- Every Source is an explicitly approved canonical original with a valid capture.
- Every content Section cites all and only the Sources represented by its independent blocks.
- Every Source block is article-body-only, maps to exactly one Source, and records included and excluded capture ranges.
- Every Section title or heading copied from the source preserves its exact visible text.
- Every formatting difference is presentation-only and provenance remains complete.
- No Source block contains page chrome, an unexplained article-body omission, addition, replacement, reorder, summary, translation, interleaving, or cross-source synthesis.
- Create and push stop on any unresolved original-content difference.
