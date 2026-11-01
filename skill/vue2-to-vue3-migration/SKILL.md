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
   area (components, store, router, Nuxt config, build).
3. **Plan.** Turn the inventory into an ordered list of changes with a rollback
   point after each phase.
4. **Migrate.** Apply the changes phase by phase: dependencies, Nuxt, router,
   store, then components.
5. **Verify.** Build, type-check and run the existing tests after every phase,
   and report what remains.

## Target presets

The user selects the target stack by naming a preset. Details, versions and the
verification procedure live in `references/presets.md`; read that file during
phase 1.

## Scope

In scope: Vue 2.6 and 2.7 projects, Options API to Composition API, TSX/JSX
components, Nuxt 2 migration, Vuex to Pinia, Vue Router 3 to 4.

Out of scope: SFC template migration, UI library migrations, visual regression
testing.
