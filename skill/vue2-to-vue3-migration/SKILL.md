---
name: vue2-to-vue3-migration
description: Migrate Vue 2 projects to Vue 3 with a selectable target stack (presets - stable, legacy-nuxt3, custom). Covers Options API to Composition API, TSX/JSX render functions, Nuxt 2 to Nuxt 4 (or 3), Vuex to Pinia, and Vue Router 3 to 4/5. Use this skill whenever the user mentions upgrading, migrating, porting or modernizing a Vue 2 or Nuxt 2 codebase, Vue.extend, Vuex stores, vue-router 3, @nuxt/bridge, Vue 2 end of life, or asks which Vue 3 or Nuxt version to move to, even if they never say "migration skill".
---

# Vue 2 to Vue 3 migration

This skill migrates a Vue 2 codebase to Vue 3 in small, verifiable steps. The
user chooses the target stack through a preset, and the skill adapts the
migration plan to that choice.

## Why the process is phased

A migration touches the framework, the router, the store and the meta-framework
at the same time. When all of them change in one pass, a failing build gives no
hint about which change broke it. Working in phases, each ending with a build
and a test run, keeps every failure attributable to one change.

## Phases

1. **Select the target stack.** Pick a preset (see "Target presets") and confirm
   the real current versions against the registry.
2. **Inventory.** Scan the project and list every incompatibility, grouped by
   area (components, store, router, Nuxt config, build). For TSX/JSX components
   run `python scripts/scan_tsx.py <project-dir> --format json` from this skill's
   folder and group the findings by file and rule. The scanner is a fast first
   pass: it does not read template files or understand runtime behavior, so open
   the files it flags and check the surrounding code. The patterns it looks for
   are listed at the end of `references/tsx-jsx.md`.
3. **Plan.** Turn the inventory into an ordered list of changes with a rollback
   point after each phase.
4. **Migrate.** Apply the changes phase by phase (see "Migrating components").
5. **Verify.** Build, type-check and run the existing tests after every phase.
   Run the scanner again with `--fail-on error`; the only errors that may remain
   are files the user decided to leave alone (for example decorator-based class
   components). Report what remains.

## Target presets

The user selects the target stack by naming a preset. Details, versions and the
verification procedure live in `references/presets.md`; read that file during
phase 1.

## Migrating components

Components are the most logic-heavy part of the migration, so they get two
separate passes. Doing them separately matters because the first pass is
mechanical and the second is a redesign; mixing them makes a regression
impossible to attribute.

1. **Make components run on Vue 3.** Read `references/tsx-jsx.md` and apply it
   to every `.tsx`, `.jsx` and `render()` component, keeping the Options API
   structure. Also rename `beforeDestroy` to `beforeUnmount` and `destroyed` to
   `unmounted`. Update the callers of every component whose props or events
   changed, not only the component itself.
2. **Convert to Composition API, only if the user asked.** Read
   `references/options-to-composition-tsx.md` and convert one component per
   commit. Skip this pass when the user wants to keep the Options API.

If a file uses `vue-property-decorator` or `vue-class-component`, stop and ask
the user how to proceed; these libraries are not covered by the references.

## Scope

In scope: Vue 2.6 and 2.7 projects, Options API to Composition API, TSX/JSX
components, Nuxt 2 migration, Vuex to Pinia, Vue Router 3 to 4.

Out of scope: SFC template migration, UI library migrations, visual regression
testing.

Not yet covered by references: Nuxt 2 configuration and data fetching, Vuex to
Pinia, Vue Router 3 to 4. For these areas, say so to the user and follow the
official migration guides until the references exist.
