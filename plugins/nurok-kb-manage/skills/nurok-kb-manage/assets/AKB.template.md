# <Knowledge Base Title>

<One-sentence description of the curated knowledge base.>

## Scope Contract

This KB helps <audience> answer <question family> using <evidence types>, within <explicit boundaries>.

### Supported Questions

- <Question family one>
- <Question family two>

### In Scope

- <Included entity, topic, source type, time, or language boundary>

### Out Of Scope

- <Excluded material and why it does not serve this KB>

### Borderline Cases

| Case | Decision | Reason |
| --- | --- | --- |
| Substantive product release with technical design detail | Review | Include only when it adds durable knowledge inside the scope. |
| Routine changelog or patch note | Exclude | It records transient operations rather than durable knowledge. |

## Evidence Policy

- Treat each URL or capture as a source, not automatically as a section.
- Preserve canonical URL, publisher or author, capture time, and content hash.
- Prefer the newest successful capture for duplicate canonical URLs unless historical comparison is in scope.
- Reject failed, empty, duplicated, or materially corrupted captures.
- Keep attribution visible when several sources contribute to one topic section.

## Topic Taxonomy

| Section | Retrieval Purpose | Include | Exclude |
| --- | --- | --- | --- |
| <Stable topic> | <Questions this section should answer> | <Material that belongs> | <Nearest material that does not belong> |

## Section Policy

- Declare whether sections represent topics, documents, records, reports, investigations, or another stable retrieval unit.
- For topic-oriented KBs, map every new source to the most specific existing topic before proposing a new section.
- Create a section only for a durable, distinct retrieval intent that cannot fit an existing section coherently.
- Use names stable for the declared retrieval unit; avoid article titles, dates, releases, or campaigns for topic-oriented sections.
- Keep publisher, author, date, source type, and URL in metadata or provenance unless they define the KB scope.
- Preserve section IDs across wording changes.
- Document source mappings when splitting, merging, or retiring sections.

## Content Assembly

- Organize topic content by claims or source subheadings appropriate to this corpus.
- Preserve per-source attribution and provenance.
- Do not duplicate a full source across sections; use a primary mapping and concise cross-references.
- <Define ordering, deduplication, language, and freshness conventions.>

## Update Protocol

1. Inventory candidate sources and deduplicate canonical URLs.
2. Record `include/exclude/hold`, scope, target section, and rationale for every candidate.
3. Review mappings to existing sections before approving any new section.
4. Update this document before implementing a scope or taxonomy change.
5. Regenerate deterministically and run focused tests plus OpenAKB validation.

## Quality Gates

- Every included source satisfies an in-scope rule.
- Every content section has a stable topic and non-empty description.
- Section growth matches the declared retrieval unit; topic-oriented KBs do not create sections mechanically per source.
- New, split, merged, renamed, and retired sections have explicit rationales.
- Provenance remains complete and auditable.
