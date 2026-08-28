# Update An Existing KB

Read this reference whenever a namespace, owner/slug, KB ID, or existing remote record identifies the target.

Do not block a historical KB's nonstructural repair or recovery solely because `.nurok` is absent. Preserve its established hierarchy, Section classes, mappings, and stable identities. Before changing any of those structural responsibilities, bootstrap and approve `.nurok/scope.md` and `.nurok/structure.md` through [scope-and-structure.md](scope-and-structure.md).

## Discover The Current CLI Workflow

Before using the CLI, inspect the installed command surface:

```bash
nurok --version
nurok kb --help
nurok kb <command> --help
```

Continue through nested help for snapshot, source-registry, or other subcommands. Use only commands and arguments shown by the installed version. Discover current defaults, conflicts, target forms, output and pagination structures, overwrite behavior, metadata synchronization, and Descriptor write-back behavior at execution time.

## Acquire The Working Copy

When the target is remote and no maintained local working copy exists, use the current CLI's supported detach or pull operation into a new authorized destination. Do not reconstruct an existing KB from search results or metadata.

Before any operation that may write local files:

1. Inventory the destination, uncommitted changes, `openakb.json`, and the generator or other source of truth.
2. Read the relevant command help and identify every overwrite, conflict, force, and write-back behavior it documents.
3. Stop unless replacement of each affected local file is authorized.
4. After execution, re-read and diff `openakb.json` and every changed artifact.

Do not assume a pull preserves or overwrites a field merely because an earlier CLI version behaved that way.

## Establish The Baseline

Use the current CLI's supported read operations to resolve and record:

- KB ID, owner/slug, endpoint, state, visibility, and live revision;
- title, description, summary, prompts, tags, and language;
- local namespace and Descriptor ID;
- source, section, root, content, and integrity-stamp counts;
- source and publishing copy locations;
- active, failed, or resumable snapshots associated with the update.

Inspect revision and snapshot history rather than inferring it from the current record. Follow pagination according to the installed command's actual structured output until exhaustion. Require local and remote identity to agree before mutation. Preserve live KB visibility unless the user explicitly requests a change.

## Plan The Delta

Require a valid immutable capture for every added Source and confirm that it is explicitly approved or objectively satisfies the approved scope inclusion rule. A pending scope amendment cannot authorize KB inclusion. Record added and removed documents, Section-class responsibility, Source-block-to-Section mappings, exact selected ranges, structurally excluded page-chrome ranges, presentation-only formatting changes, summary-title changes, metadata changes, provenance changes, and unexpected count changes. Keep discovery and auxiliary material outside the KB.

Preserve stable typed IDs, namespace, capture times, document boundaries, Source order, and unchanged integrity data. Keep a Section ID only while its approved class and stable retrieval responsibility remain the same; mint new IDs for material responsibility changes, splits, or merges. Project approved scope or structure changes into `AKB.md` before changing the generator. Stop if `.nurok`, `AKB.md`, and `openakb.json` conflict. Avoid unrelated crawler, Source, structure, and formatting changes.

## Keep Metadata Layers Separate

Treat Descriptor metadata and remote KB-record metadata as independent states. Before publication, decide whether this operation should change either or both layers. Inspect the current publication and metadata command help to determine whether synchronization is supported, implicit, explicit, or separate.

Metadata mutation and snapshot publication may not be transactional. Save both baselines before mutation. After any failure, re-read both states and report partial success before retrying or reverting anything.

Treat source pointer visibility and KB visibility independently. Descriptor Source IDs such as `SRC-000001` are local OpenAKB citation identities; they are not Nurok registry Source identities. When registry correction is authorized:

1. Inspect the current source-registry command help.
2. Obtain each `registry_source_identity` from verified registry list or get results for the intended endpoint, owner, and KB.
3. Follow the actual pagination structure to exhaustion.
4. Update only confirmed mismatches with the reference form accepted by the installed CLI.
5. Collect per-source failures and verify the remote results.

Never derive a registry identity from `sources[].id`. Do not make the KB public merely because evidence pointers are public. Discover and use a separate current CLI operation for any authorized KB visibility change, then verify the returned target and visibility.

## Protect `openakb.json`

Treat `openakb.json` as a mixed-state artifact: corpus-owned content may coexist with platform-written namespace, revision, hash, and length data.

- Modify JSON with a structured parser and update the generator or declared source of truth, not only generated output.
- Preserve a verified namespace, remote binding, revision baseline, and unchanged integrity data.
- Preserve existing typed Source and Section IDs across deterministic regeneration.
- Do not overwrite a server-bound Descriptor with a namespaceless generated copy.
- After any CLI command that may write back state, diff the actual file and structurally reconcile platform-written fields into the maintained source of truth.
- When bytes change, treat their prior hashes and lengths as stale; when bytes do not change, preserve verified stamps.
- Compare aggregate content hashes; count equality is not proof of content equality.
- Compare every changed Source block's visible text with its selected article-body ranges. Stop on any alteration of selected content, unexplained omission relative to the approved Section-class policy, replacement, reorder, interleaving, page-chrome exclusion without structural evidence, or change that is not presentation-only formatting.

## Synchronize The Publishing Copy

Derive the publishing set from the Descriptor. Include `openakb.json` and every relative local blob referenced by `guide_uri`, section `content_uri` or `provenance_uri`, a `file` source `uri`, source `capture_uri`, or `x.ai.nurok.skill_uri`. The common simple set is `openakb.json`, `AKB.md`, and `sections/`, but it is not a complete allowlist. Do not copy unreferenced crawler code, raw archives, tests, caches, build notes, or virtual environments.

Never reference or copy `.nurok` into the publishing set. It is a local build control plane, not a formal Descriptor artifact.

Copy only changed artifacts, then compare the complete Descriptor projection before publication:

```bash
python3 <skill-dir>/scripts/audit_working_copy.py \
  --dir <working-copy> \
  --compare-dir <publishing-copy> \
  --format json
```

Require no missing, unexpected, or byte-different projected files and identical aggregate digests, then validate both copies. After the CLI writes namespace, revision, hash, or length data, reconcile the actual Descriptor into the generator-preserved source copy without losing corpus-owned changes.

## Require Update Evidence

Before publication, require valid local artifacts, a verified explicit remote target, intended metadata, preserved visibility, stable identity, verified original-content integrity, and a specific revision message. Use the current CLI's create-prevention and concurrency or revision guards. If the installed CLI cannot express the necessary identity and drift protections, stop rather than issue an unguarded mutation.

After publication, require the intended live revision and metadata, unchanged visibility unless authorized, expected source pointer projections, representative retrieved Section text matching the validated publishing copy, an inspected local Descriptor diff, and an explicit disposition for retained drafts or local differences.
