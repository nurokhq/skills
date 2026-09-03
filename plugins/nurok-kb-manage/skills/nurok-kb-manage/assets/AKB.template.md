# <Knowledge Base Title>

<One-sentence description of the approved topic, audience, use, corpus boundary, and provenance without claims about Source content.>

This guide is the human-readable projection of the approved scope and structure for this KB revision.

## Goal And Scope

- **Core goal:** <What users should retrieve, read, or accomplish>
- **Audience and primary use:** <Approved audience and use>
- **Approved corpus boundary:** <Objective, reproducible inclusion boundary>
- **Explicit exclusions:** <Material that remains outside the KB>
- **Source approval rule:** <Explicit per-Source approval or approved objective inclusion rule>

Do not describe a predefined organization mode. Keep discovery notes, auxiliary evidence, analysis, and other derived material outside the KB.

### Optional Finite-Corpus Manifest

Use this table only when the approved corpus is finite and listing every Source is useful. The formal Source list remains `openakb.json`.

| Source | Canonical URI | Immutable Capture | Document Boundary | Approval |
| --- | --- | --- | --- | --- |
| <Canonical original> | <Canonical URI> | <Hash-pinned capture> | <Whole document or explicit boundary> | <Approval evidence> |

## Structure Contract

| Section Class | Retrieval Responsibility | Source Mapping | Content Selection | Section Title | Evidence Policy |
| --- | --- | --- | --- | --- | --- |
| <Class name> | <Stable responsibility> | <One-to-one, split, reused, multi-Source, or another approved mapping> | <Whole article body or exact excerpts at provable boundaries> | <Direct summary of all visible Source blocks> | <Required evidence and provenance> |

Describe the approved root hierarchy, parent rules, stable Section identity rule, and representative structure. Different Section classes may use different mappings. The cases in this template are examples, not classification values.

## Source And Content Policy

- Use only approved canonical Sources with real immutable captures.
- Preserve every capture completely and immutably, including canonical identity, capture time, content hash, and content length.
- Select Source content only as permitted by the Section class. Preserve every selected word, punctuation mark, link target, paragraph boundary, and original order.
- Never correct, translate, rewrite, paraphrase, deduplicate, reorder, or add generated transitions, comparisons, explanations, conclusions, or cross-Source inference.
- Exclude page chrome only with structural evidence. Keep ambiguous material or hold the Source for direction.
- Keep every Source, selected range, and resulting block deterministically traceable.

## Section And Source-Block Presentation

Every content Section title directly and verifiably summarizes all Source blocks visible in that Section. It must not use hidden capture content, external information, Agent knowledge, unsupported causality, evaluation, certainty, or false consensus.

Start each independent Source block with:

```markdown
<!-- source-block:<Source ID> -->
[cite:<Source ID>]

## <Source identity label>
```

Choose the Source identity label in this order:

1. a Source title verified from its capture;
2. its canonical Source URL; or
3. its stable Source ID.

The label only distinguishes the Source block; it is not a content summary. Keep each Source in a visibly separate block. Never interleave Source prose or turn multiple blocks into a synthesized narrative.

When one Source block uses multiple noncontiguous excerpts, preserve their original order, separate them visibly without generated prose, and record every exact range separately. Never use one covering range for omitted intermediate content.

## Presentation-Only Formatting

- Add blank lines only between existing Source paragraphs.
- Render an existing Source title or heading with Markdown markers while copying its visible text exactly.
- Represent existing lists, quotations, tables, links, and code with equivalent Markdown structure.
- Separate blocks and noncontiguous excerpts without generated explanatory text.

When formatting prevents byte equality, use deterministic provenance to prove that visible Source text remains the same ordered content as the selected capture ranges.

## Provenance Contract

| Section | Source Block | Source | Selected Ranges | Excluded Page-Chrome Ranges And Evidence | Order |
| --- | --- | --- | --- | --- | --- |
| <Section ID> | <Stable block ID or index> | <Source ID> | <Exact ranges or equivalent provenance> | <Ranges plus DOM, template, or repetition evidence> | <Sequence> |

Keep Descriptor `source_ids`, Source-block markers, inline citations, provenance Source IDs, and block order aligned.

## Update Protocol

1. Confirm that every added Source is approved or matches the approved inclusion rule and has valid immutable evidence.
2. Confirm that changes remain within the approved scope, structure, Section-class responsibility, and stable identity rules.
3. Update the Source-block map, exact selected ranges, exclusions, summary titles, and provenance without changing unrelated content.
4. Regenerate formal artifacts deterministically from the approved contracts and declared source of truth.
5. Compare every visible Source block with its selected ranges, run focused tests and the bundled audit, and complete current OpenAKB validation.
6. Build and verify a separate Descriptor-projected publishing copy before any authorized push.

## Quality Gates

- Every Source is approved canonical evidence with a valid immutable capture.
- Every Section follows its approved class, mapping, evidence policy, and stable retrieval responsibility.
- Every content Section title is supported by all and only its visible Source blocks.
- Every Source block starts with the required marker and citation, has a non-summary Source identity label, and maps to exactly one Source.
- Every selected or excluded range has deterministic provenance; noncontiguous excerpts use separate ranges.
- No Source block contains alteration, unsupported omission, reordering, interleaving, summary prose, translation, or cross-Source synthesis.
- The publishing copy contains the complete formal Descriptor projection and excludes local process artifacts.
- Create, update, and push stop on any unresolved approval, authority, provenance, content-integrity, identity, or validation conflict.
