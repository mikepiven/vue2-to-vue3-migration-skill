# vue2-to-vue3-migration-skill

Claude agent skill for migrating Vue 2 projects to Vue 3 with a selectable target stack. It covers TSX/JSX components, Options API to Composition API, Nuxt 2 to Nuxt 4 (or 3), Vuex to Pinia, and Vue Router 3 to 4/5, and ships with a breaking-change scanner and tests.

> Status: work in progress. TSX/JSX components are covered end to end. Nuxt, Pinia and Router references are still to come (see the table below).

![tests](https://github.com/mikepiven/vue2-to-vue3-migration-skill/actions/workflows/test.yml/badge.svg)

## What it does

When you ask Claude to migrate a Vue 2 or Nuxt 2 codebase, the skill gives it a phased process:

1. **Select a target preset** and verify the real current versions against the npm registry.
2. **Inventory** every incompatibility with `scripts/scan_tsx.py`.
3. **Plan** an ordered list of changes with a rollback point after each phase.
4. **Migrate** in two passes: first make components run on Vue 3, then (optionally) convert to Composition API.
5. **Verify** with build, type-check, tests and a final scanner run.

Splitting the work into passes keeps every failure attributable to one change.

## Target presets

| Preset | Vue | Nuxt | Pinia | Router |
|--------|-----|------|-------|--------|
| `stable` (default) | 3.5 | 4 | 4 | bundled with Nuxt (5 without Nuxt) |
| `legacy-nuxt3` | 3.5 | 3 (end of life since 2026-07-31, the skill warns) | 4 | bundled with Nuxt |
| `custom` | you choose | you choose | you choose | you choose |

Version facts go stale, so the skill tells Claude to re-check them against the registry before migrating. See `skill/vue2-to-vue3-migration/references/presets.md`.

## Coverage

| Area | Status |
|------|--------|
| TSX/JSX: vnode format, slots, `v-model`, emits, functional components, directives, TypeScript config | done |
| Options API to Composition API for TSX components | done |
| Breaking-change scanner for TSX, `package.json`, `tsconfig.json` | done |
| Nuxt 2 to Nuxt 4 / 3 (config, data fetching, plugins, middleware) | planned |
| Vuex to Pinia | planned |
| Vue Router 3 to 4 | planned |

Out of scope: SFC `<template>` migration, UI library migrations, visual regression testing.

## Install

**Claude Code:** copy the skill folder into your skills directory.

```bash
git clone https://github.com/mikepiven/vue2-to-vue3-migration-skill.git
cp -R vue2-to-vue3-migration-skill/skill/vue2-to-vue3-migration ~/.claude/skills/
```

**Claude.ai:** zip the `skill/vue2-to-vue3-migration` folder and upload it in the Skills section of the Claude settings.

## Usage

Just ask. The skill triggers on requests like:

- "Migrate this Vue 2 project to Vue 3, stable preset, keep the Options API."
- "We still use `Vue.extend` and Vuex 3. What do we need to change to get to Vue 3?"
- "Move our Nuxt 2 app off `@nuxt/bridge`."

You can also run the scanner directly (Python 3.9+, standard library only):

```bash
python skill/vue2-to-vue3-migration/scripts/scan_tsx.py path/to/project
python skill/vue2-to-vue3-migration/scripts/scan_tsx.py path/to/project --format json --fail-on error
```

## Tests

```bash
python -m unittest discover -s tests -v
```

The suite checks every scanner rule against matching and non-matching snippets, runs the scanner on a Vue 2 TSX fixture and asserts the exact findings per file, asserts that the hand-written Vue 3 result in `tests/fixtures/expected-vue3` produces zero findings, and verifies that every scanner rule points at an existing heading in the references.

Behavioral tests for Claude itself live in `skill/vue2-to-vue3-migration/evals/` in the `claude plugin eval` layout (prompt, input files, graders).

## Repository layout

```
skill/vue2-to-vue3-migration/
  SKILL.md                  workflow and preset selection
  references/               presets, TSX/JSX, Options to Composition
  scripts/scan_tsx.py       breaking-change scanner
  evals/                    behavioral test cases
tests/                      scanner tests and golden fixture
docs/SCOPE.md               scope and target version facts
```

## License

MIT
