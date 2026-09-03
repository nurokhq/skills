# Control Source Disclosure

Read this reference before inspecting, declaring, changing, or publishing Source pointer visibility or provenance.

## Classify Source Visibility

Treat a Source as public unless Descriptor metadata or verified Source-registry state explicitly marks it private. Any explicit private marker wins. Keep Source visibility independent from KB record visibility: a private KB does not make its Sources private, and public evidence does not make the KB public.

Descriptor Source IDs such as `SRC-000001` are local OpenAKB citation identities, not Nurok registry Source identities. Use only a registry identity returned for the verified endpoint, owner, and KB when a separately authorized registry operation requires one.

## Declare Public Pointers

Use this Descriptor extension when declaring public pointer visibility:

```json
{
  "x": {
    "ai.nurok": {
      "pointer_visibility": "public"
    }
  }
}
```

Recommend explicit public pointer visibility for a `url` Source when its canonical URL and identifying metadata are already public and safe to disclose. A recommendation authorizes neither a remote Source-registry mutation nor a KB visibility change.

## Protect Private Provenance

For every explicitly private Source, keep provenance artifacts non-identifying. Refer to it only by its opaque stable Source ID and the Section, block, range, and order mapping required for deterministic traceability. Omit its canonical or capture URL, title, provider or owner name, filename or path, visible Source-block label, and every other source-identifying field.

Change the generator or declared source of truth, then regenerate only the affected Descriptor or provenance artifacts. Update every hash and length that describes changed bytes.

## Complete The Disclosure Check

For every affected Source, verify and report:

- the evidence used to classify its visibility;
- intentional public pointer metadata or non-identifying private provenance;
- updated integrity stamps for every changed artifact;
- byte-identical out-of-scope artifacts; and
- whether remote state was read or mutated.

For a local-only repair, complete with no remote read or mutation and stop before publishing-copy preparation. For an authorized remote operation, verify the endpoint, authenticated identity, target, operation, and resulting visibility before completion.
