# Publishing Nurok Skills to Codex Plugins

`nurok-skills` can be distributed in two ways:

1. Publish it as a Git-backed Codex marketplace for direct installation.
2. Submit it to OpenAI's universal Plugins Directory for public discovery in ChatGPT and Codex.

These are separate distribution channels. A Git marketplace is suitable for development, testing, and direct distribution. Publishing in the official directory requires OpenAI review.

## Publish Through the GitHub Marketplace

The repository already contains the required marketplace and plugin structure:

- `.agents/plugins/marketplace.json` defines the `nurok` marketplace.
- `plugins/nurok-skills/.codex-plugin/plugin.json` defines the `nurok-skills` plugin.
- `plugins/nurok-skills/skills/` contains its bundled skills.

At the time of writing, commit `d697e48` exists only in the local repository. Push it before attempting a remote installation:

```bash
git push origin main
```

Users can then install the development version:

```bash
codex plugin marketplace add nurokhq/skills --ref main
codex plugin add nurok-skills@nurok
```

### Publish a Stable Version

For stable releases, update the `version` in `plugins/nurok-skills/.codex-plugin/plugin.json`, commit the change, and publish a matching Git tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Users can pin the marketplace to that release:

```bash
codex plugin marketplace add nurokhq/skills --ref v0.1.0
codex plugin add nurok-skills@nurok
```

To refresh an existing marketplace snapshot:

```bash
codex plugin marketplace upgrade nurok
```

## Publish to the Official Plugins Directory

GitHub distribution does not automatically list the plugin in the public Plugins Directory. To make `nurok-skills` discoverable from supported ChatGPT and Codex plugin surfaces, submit it through the OpenAI plugin submission portal.

### Prerequisites

1. Use the OpenAI Platform organization that will own the plugin.
2. Ensure the submitter has **Apps Management: Write** permission.
3. Complete developer or business identity verification for Nurok.
4. Prepare public URLs for the website, support page, privacy policy, and terms of service.
5. Prepare production-ready plugin branding, including a logo or icon.

### Submission Process

1. Open the [OpenAI plugin submission portal](https://platform.openai.com/plugins).
2. Select **Create plugin**.
3. Select **Skills only** for the current `nurok-skills` package.
4. Upload the final skill bundle using the same file tree that was tested locally.
5. Complete the public listing and publisher information.
6. Add realistic starter prompts.
7. Provide at least five positive test cases and three negative test cases.
8. Select the supported countries or regions.
9. Add release notes and complete the policy attestations.
10. Select **Submit for Review**.
11. After approval, publish the approved version from the portal.

Once published, the plugin appears in the universal Plugins Directory shared by ChatGPT and Codex.

## Remaining Official-Publishing Work

Before submitting the current plugin to the official directory, add or prepare:

- A public privacy policy URL.
- A public terms-of-service URL.
- A public support URL; `support@nurok.ai` is a contact email, not a support web page.
- Plugin logo and icon assets.
- Five positive review test cases.
- Three negative review test cases.

The corresponding manifest fields should include `privacyPolicyURL` and `termsOfServiceURL`. Publisher names, domains, support details, and policy pages should consistently identify Nurok so they match the verified business identity.

## Recommended Release Order

1. Push the current repository to `https://github.com/nurokhq/skills`.
2. Test installation from the `main` Git marketplace.
3. Publish and verify a tagged `v0.1.0` release.
4. Add the legal URLs, support page, and brand assets.
5. Prepare the required positive and negative review cases.
6. Submit the skills-only plugin to OpenAI for review.
7. Publish it in the universal Plugins Directory after approval.

## Official References

- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Submit plugins](https://developers.openai.com/plugins/deploy/submission)
