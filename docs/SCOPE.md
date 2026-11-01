# Skill scope

Status: draft, checked against public sources on 2026-11-01.

## In scope

| Area | From | To |
|------|------|----|
| Framework | Vue 2 (2.6 / 2.7) | Vue 3 (target version is selectable) |
| Component style | Options API | Composition API (`defineComponent` + `setup`) |
| Component format | TSX / JSX render functions | TSX / JSX for Vue 3 (`@vue/babel-plugin-jsx`) |
| Meta-framework | Nuxt 2 | Nuxt (target version is selectable, see below) |
| State management | Vuex 3 | Pinia |
| Routing | Vue Router 3 | Vue Router 4 (5 is a drop-in for 4) |

## Out of scope (for now)

- SFC `<template>` migration (the skill targets TSX/JSX components)
- UI library migrations (Vuetify, Element, etc.)
- Build tool migration beyond what Nuxt requires
- Visual / e2e regression testing of the migrated app

## Target version facts that shape the design

These are volatile. The skill must tell Claude to re-verify them at migration
time instead of trusting this table.

| Item | Status on 2026-11-01 | Source |
|------|----------------------|--------|
| Vue 2 | EOL since 2023-12-31, last release 2.7.16 | Vue docs |
| Vue 3 | 3.5.x is stable, 3.6 is in beta (Vapor Mode) | vuejs/core releases |
| Nuxt 2 | EOL since 2024-06-30 | Nuxt roadmap |
| Nuxt 3 | **EOL since 2026-07-31** | Nuxt roadmap |
| Nuxt 4 | Current stable line (4.5.x), Nuxt 5 not yet released | Nuxt roadmap, nuxt/nuxt releases |
| Vue Router | 5.x is a drop-in upgrade from 4 when file-based routing plugins are not used | router.vuejs.org |
| Pinia | 4.x current, ESM-only, requires `@vue/devtools-api` | pinia releases |

## Design consequence

The "target version" choice is a **preset** (a combination of Vue, Nuxt, Pinia
and Router versions), not a single number. A Nuxt 2 → Nuxt 3 preset is allowed
but the skill warns that Nuxt 3 is end-of-life.
