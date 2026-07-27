# Scope And Curation

Read this reference before creating a KB, changing its boundary, ingesting a source batch, or restructuring sections.

## Separate The Units

- **Corpus**: all material available for review.
- **Knowledge base**: selected material serving one coherent audience and family of questions.
- **Source**: one evidence unit, such as an article, post, paper, file, or capture.
- **Section**: a stable retrieval topic supported by one or more sources.

Do not mirror crawler layout or create one section per URL by default. Preserve article-level provenance when several articles contribute to one section.

## Define The Boundary

Write one sentence before designing sections:

```text
This KB helps <audience> answer <question family> using <evidence types>, within <explicit boundaries>.
```

Keep material together only when audience, question family, evidence policy, and taxonomy are coherent.

- Separate individuals from organizations unless the KB explicitly studies their relationship.
- Split one entity's corpus when it serves independent question families needing different inclusion rules or taxonomies.
- Group different publishers when their sources serve the same scope and comparison is useful.
- Do not use directory layout, publisher initials, crawl date, source count, request size, or platform caps as semantic boundaries.
- Treat unavoidable technical shards as physical partitions of one declared scope, not as subject taxonomy.

Prefer a narrow, explicit scope over an archive that cannot state what questions it answers.

## Define The Local Convention

Write the KB-specific contract in `AKB.md` using `assets/AKB.template.md`. Include purpose, audience, question families, inclusion and exclusion rules, borderline cases, source quality, taxonomy, section evolution, content assembly, provenance, freshness, and quality gates.

Update `AKB.md` before the generator whenever scope or taxonomy changes. Keep universal Nurok workflow rules in this skill rather than copying them into every KB.

## Curate Every Source

Produce a disposition before adding a source:

```text
source | include/exclude/hold | scope | target section | new section? | rationale
```

Usually include durable research, technical explanation, architecture, engineering, evaluation, safety, security, governance, tutorials, postmortems, design rationale, and operational lessons. Include a product announcement only when it contributes lasting technical or strategic substance.

Unless release history is the declared scope, exclude routine changelogs, patch notes, version bumps, minor feature announcements, event promotion, hiring pages, navigation pages, sales pages, thin SEO content, duplicates, syndicated copies, failed captures, empty captures, parser-corrupted text, and out-of-scope material.

Hold ambiguous sources for review. Do not create a `Miscellaneous` section to avoid a decision.

## Map Sources Merge-First

Offer each included source to the most specific existing topic whose description and retrieval intent fit. Create a section only when all are true:

1. The material is in scope.
2. No existing section can absorb it coherently.
3. The topic has a durable name that is not an article title, date, release, or campaign.
4. It serves a distinct user question or retrieval intent.
5. Its boundary can be described with substantive evidence.

One exceptional source may seed an important topic likely to recur; otherwise hold it. Use source titles as headings inside topic content when useful, while retaining attribution and provenance. Map cross-cutting material to one primary section and add a concise cross-reference only when it improves retrieval without duplicating the full source.

## Evolve Sections Deliberately

- Preserve stable topic IDs across wording changes.
- Split a section when it repeatedly serves independent retrieval intents.
- Merge sections whose boundaries overlap or cannot be applied consistently.
- Retire a section only after remapping its sources and documenting the migration.
- Keep hierarchy shallow unless another level materially improves navigation.
- Keep author, publisher, date, source type, and URL in metadata or provenance unless they define the scope.

For every batch, review dispositions, existing-topic mappings, new-section proposals, structural migrations, count changes, duplicate URLs, and provenance gaps. Use source-to-section growth only as a diagnostic for topic-oriented KBs. When `AKB.md` declares a document, record, repository, report, investigation, standard, or case as the stable retrieval unit, one section per unit or several sections supported by one aggregate provenance source can be intentional.
