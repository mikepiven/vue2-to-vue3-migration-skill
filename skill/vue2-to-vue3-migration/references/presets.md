# Target presets

Read this file during phase 1. A preset is a combination of Vue, Nuxt, Pinia and
Vue Router versions that are known to work together. The user picks one by name.

## Contents

- Presets
- How to choose when the user did not say
- Verify versions before migrating
- Known facts (checked 2026-11-01)

## Presets

### stable

The default. Moves the project to currently supported lines.

| Package | Target |
|---------|--------|
| vue | ^3.5 |
| nuxt | ^4 |
| pinia | ^4 (with `@pinia/nuxt` and `@vue/devtools-api`) |
| vue-router | bundled with Nuxt; do not install it separately in a Nuxt project |

For a plain Vue project without Nuxt, use `vue-router` ^5. It is a drop-in upgrade
from 4 when no file-based routing plugin is used.

### legacy-nuxt3

For teams that cannot move to Nuxt 4 yet. Same as `stable`, but with `nuxt` ^3.

Always tell the user before migrating: Nuxt 3 reached end of life on
2026-07-31 and no longer receives security fixes. Offer `stable` once, and
continue with `legacy-nuxt3` if they confirm.

### custom

The user names exact versions. Check them against each package's
`peerDependencies` (see below) and report any conflict before changing files.

## How to choose when the user did not say

Ask one question that names the presets and recommends `stable`. If no answer is
possible (for example in a non-interactive run), use `stable` and state the
assumption at the top of the plan.

## Verify versions before migrating

Versions in this repository go stale. Before phase 2, run these commands in the
user's project or any scratch directory and use their output, not this file:

```bash
npm view vue version
npm view nuxt version
npm view nuxt@3 version
npm view pinia version
npm view pinia peerDependencies
npm view vue-router version
npm view @pinia/nuxt peerDependencies
```

Also open the official Nuxt roadmap (https://nuxt.com/docs/3.x/community/roadmap)
to confirm which Nuxt lines are still supported. If the registry or roadmap
disagrees with the table below, trust the registry and tell the user.

## Known facts (checked 2026-11-01)

- Vue 2 reached end of life on 2023-12-31; the last release is 2.7.16.
- Vue 3.5.x is the stable line; 3.6 is in beta.
- Nuxt 2 reached end of life on 2024-06-30. Nuxt CLI 4 no longer supports Nuxt 2
  or `@nuxt/bridge`.
- Nuxt 3 reached end of life on 2026-07-31. Nuxt 4 is the current stable line.
- Vue Router 5 is a transition release that merges file-based routing into the
  core package; projects on Vue Router 4 without it can upgrade with no code
  changes.
- Pinia 4 is ESM-only and requires `@vue/devtools-api` to be installed.
