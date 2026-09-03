# Approve Scope And Derive Structure

Read this reference before scaffolding a new KB, generating its complete Section set, or performing a structural redesign of an existing KB.

## Separate Authorization From Structure

Do not ask the user to choose a predefined organization mode. Derive concrete structure rules from the KB's approved goal, audience, use, corpus boundary, Source shape, retrieval needs, content risk, and visibility requirements. Treat document-oriented, task-oriented, and layered arrangements only as non-exhaustive examples.

For a new KB or structural redesign:

1. Inspect the authorized working root, repository instructions, existing artifacts, candidate Sources, and locally discoverable facts without mutating state.
2. Ask first for the core goal and primary use. Ask one unresolved factual or decision question at a time.
3. Establish the audience, objective corpus boundary, exclusions, retrieval needs, and content risks.
4. Optionally perform a limited pilot capture only under separate capture authority. Keep it provisional and do not treat it as scope or structure approval.
5. Record and obtain approval for the concrete scope.
6. Derive the hierarchy, Section classes, Section–Source mappings, content-selection rules, title rules, evidence policies, and stable identity rules.
7. Explain the derivation and show a representative structure sample.
8. Record and obtain approval for the concrete structure.
9. Scaffold, generate the complete Section set, or restructure only after the relevant approvals exist.

Approved scope authorizes a full new-KB batch capture within its Source boundary. It does not authorize scaffolding or complete Section generation before structure approval.

## Keep The Build Control Plane In `.nurok`

Confirm the user-authorized KB working root before creating `.nurok`. Keep it beside an existing or subsequently created `openakb.json`.

Keep every KB-creation process file, script, configuration, state file, log, report, pilot output, and publishing-preparation artifact inside `.nurok`. Reserve `.nurok/scope.md` and `.nurok/structure.md` as the two fixed contract files; do not prescribe its internal subdirectory names.

Keep formal OpenAKB artifacts in their standard locations. Never reference `.nurok` from the Descriptor, copy it directly into a publishing copy, or publish it. Whether non-sensitive `.nurok` material enters version control is a project or user decision. Never commit credentials, private Source content, or sensitive logs.

Apply these authority layers:

- `.nurok/scope.md` and `.nurok/structure.md` are authoritative for build authorization, design decisions, and approval history.
- `openakb.json` is authoritative for the current formal Sources, Sections, entity relationships, and Descriptor file projection.
- `AKB.md` is the human-readable projection of the approved contracts for the current build or published revision.

Synchronize `AKB.md` from the current approved contracts before building. Stop on a conflict among these layers; do not choose one silently or overwrite another. Reading a published historical KB does not require `.nurok`. Nonstructural repair or recovery of a historical KB may proceed without it under the existing-KB rules.

## Record The Scope Contract

Use compact YAML frontmatter and Markdown in `.nurok/scope.md`. Record:

- `status: draft | approved` and the current approval record;
- the core goal, audience, and primary use;
- an objective approved-corpus boundary and explicit exclusions;
- the canonical-original and immutable-evidence requirements;
- material user decisions; and
- whether this is a new KB or structural redesign.

Do not record an organization mode or classification label. Do not impose a fixed questionnaire, fixed length, acceptance questions, manifest hash, or complete Source manifest. A finite corpus may include a manifest. An open corpus must instead use bounded, reproducible inclusion rules; reject criteria such as "all relevant" or "all important" material.

## Record The Structure Contract

Use compact YAML frontmatter and Markdown in `.nurok/structure.md`. Record:

- `status` and the current approval record;
- the derivation rationale;
- the root hierarchy, parent rules, and Section classes;
- each class's retrieval responsibility, Source mapping, content-selection rule, Section-title rule, and evidence policy;
- stable Section identity rules;
- provenance and visible Source-block isolation rules; and
- the user-approved representative structure sample.

Do not record a predefined organization type or enumerate every final Section in advance. The generator may expand the approved rules deterministically.

Derive rather than classify. Useful arrangements include, but are not limited to:

- one Source per Section for preserving and browsing documents;
- ordered Sections split at original boundaries for a long Source;
- one task-focused Section containing exact evidence from one or more visibly separate Sources;
- layered navigation combining document-preserving and evidence-focused Section classes; and
- one Source supporting multiple Sections through separately traced excerpts.

One KB may use different mappings for different approved Section classes. Never apply one class's rules silently to another.

## Record Approval Exactly

Treat either of these as approval evidence:

- the user explicitly approves the exact displayed scope or structure in the current conversation; or
- the corresponding `.nurok` contract has `status: approved`, `approved_by`, and `approved_at`, and its content matches the current task.

Write `status: approved`, `approved_by`, and `approved_at` only when one of those evidence forms exists and covers the current file content. Recording an approval is not Agent authority to grant one. Otherwise keep or set `status: draft`.

Use `approved_by: user` when the approver's identity cannot be established reliably. Never infer it from the operating-system username, Git configuration, or a remote account. Use an ISO 8601 timestamp with a timezone for `approved_at`.

When current instructions conflict with an approved contract, identify the conflict and ask whether the user is revising it. Preserve approval history, set the affected contract to `draft`, and wait for explicit approval of the revised content.

## Amend Scope Without Hiding Drift

Treat a scope amendment as incremental approval of an expanded inclusion rule or boundary. Before approval, keep the proposal in the conversation or another `.nurok` process record; do not rewrite the approved scope body. The existing scope remains valid, but the pending amendment cannot authorize KB batch capture, Descriptor inclusion, or KB construction for a proposed Source.

An independently authorized single-Source capture may still proceed under its own boundary. It does not approve that Source for the KB.

After explicit approval, update the complete scope text, append a new approval record, retain the history, and keep the current status `approved`. If the change also affects the core goal, audience, primary use, content risk, visibility, or another mandatory drift condition, use the full draft-and-reapproval flow instead.

## Preserve Stable Knowledge Units

Define a deterministic identity rule for every Section class. A knowledge unit remains the same when its Section class and predeclared stable retrieval responsibility remain the same. Its title, current excerpts, Source count, and exact evidence ranges do not automatically define its identity.

Possible identity rules include:

- Source ID plus whole-document responsibility;
- Source ID plus an original structural unit or approved stable partition key for a split document;
- an approved question, topic responsibility, or workflow step for an evidence Section; and
- an approved navigation responsibility for a parent Section.

Do not use a currently observed byte range as the sole stable identity for a document segment. Keep the Section ID when the identity rule still resolves to the same responsibility and the evidence policy remains satisfied, even if the evidence set changes. Mint a new ID when the Section class or responsibility materially changes, or when responsibilities split or merge. Keep this identity state in `.nurok` or the generator; do not add an OpenAKB schema field.

## Handle Drift

Set the affected scope or structure contract to `draft` and require explicit reapproval when any of these changes:

- audience, core goal, or primary use;
- main organization axis, hierarchy, Section classes, or Section–Source mapping rules; or
- evidence policy, content risk, or visibility boundary.

Preserve prior approval records as history, but do not let old approval metadata represent approval of new content.

Source-category, publisher, language, time, or authority-boundary expansion does not by itself require full structure reapproval, but it still requires approval through the scope rule or amendment process. Document-boundary, allowed-excerpt, and same-knowledge-unit excerpt or summary-title changes likewise require their applicable authorization, provenance update, and technical validation without automatically forcing full structure reapproval.
