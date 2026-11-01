# TSX/JSX: Vue 2 to Vue 3

Read this file when the project contains `.tsx` or `.jsx` components, or
`render()` functions that call `h`. These changes are mandatory: the code does
not run on Vue 3 until they are applied. Converting Options API to Composition
API is a separate, optional step described in `options-to-composition-tsx.md`.

## Contents

- Strategy: make it run first, restructure second
- Tooling swap
- Vnode format: nested data object becomes flat props
- Mapping table
- Complete before and after example
- Slots
- v-model and .sync
- Events, emits and .native
- Refs
- Functional components
- Attributes and listeners
- Directives
- TypeScript configuration
- Detection patterns for the inventory phase

## Strategy: make it run first, restructure second

Keep each component in the Options API while fixing the items below. A
component that runs on Vue 3 with its old structure gives a stable baseline, so
when a later Composition API rewrite breaks something, the cause is the rewrite
and not the framework upgrade.

## Tooling swap

| Vue 2 | Vue 3 |
|-------|-------|
| `@vue/babel-preset-jsx`, `@vue/babel-plugin-transform-vue-jsx`, `babel-helper-vue-jsx-merge-props` | `@vue/babel-plugin-jsx` (Babel) or `@vitejs/plugin-vue-jsx` (Vite) |
| `vue-tsx-support` | remove; use `defineComponent` typing |
| `vue-class-component`, `vue-property-decorator` | not part of this migration; flag every file that uses decorators and ask the user how to proceed |

Nuxt compiles `.tsx` and `.jsx` through its Vite pipeline. Plugin options are
passed through the `vite.vueJsx` key of `nuxt.config.ts`; confirm the current
option name in the Nuxt documentation for the chosen preset before editing the
config.

## Vnode format: nested data object becomes flat props

Vue 2 groups everything into a data object (`attrs`, `props`, `on`, `domProps`,
`nativeOn`, `scopedSlots`). Vue 3 passes one flat object, and the runtime decides
whether a key is a prop, an attribute, a DOM property or a listener. This is the
root cause of most JSX breakage, so check every JSX attribute that begins with
`on`, `nativeOn`, `domProps`, `attrs`, `props` or `scopedSlots`.

Why it matters: a Vue 2 prefix such as `domPropsInnerHTML` is not an error in
Vue 3. It is silently rendered as an attribute named `domPropsInnerHTML`, so the
build passes and the page is wrong. Search for these prefixes explicitly.

## Mapping table

| Vue 2 JSX | Vue 3 JSX |
|-----------|-----------|
| `render(h) { ... }` | `render() { ... }` (no `h` parameter; import `h` from `vue` only if you call it by hand) |
| `this.$createElement` | `h` imported from `vue` |
| `nativeOnClick={fn}` on a component | `onClick={fn}` (listener falls through to the root element) |
| `domPropsInnerHTML={html}` | `innerHTML={html}` |
| `domPropsValue={v}` | `value={v}` |
| `attrs={{ id: 'a' }}` or `{...{ attrs: { id: 'a' } }}` | `id="a"` or `{...{ id: 'a' }}` |
| `{...{ props: { a: 1 }, on: { change: fn } }}` | `{...{ a: 1, onChange: fn }}` |
| `scopedSlots={{ default: (p) => <b>{p.x}</b> }}` | `v-slots={{ default: (p) => <b>{p.x}</b> }}` |
| `this.$scopedSlots.foo(p)` | `this.$slots.foo?.(p)` |
| `this.$listeners` | removed; listeners are inside `this.$attrs` |
| `this.$children` | removed; use refs or provide/inject |
| `refInFor` | removed; use a function ref |
| `vModel={this.value}` | `v-model={this.value}` |
| `onClick={...}` with `.stop` or `.prevent` helper | `onClick={withModifiers(fn, ['stop', 'prevent'])}` |
| `Vue.extend({...})` | `defineComponent({...})` |
| `slot="name"` attribute | removed; pass named slots with `v-slots` |

## Complete before and after example

Vue 2:

```tsx
import Vue from 'vue'
import BaseButton from './BaseButton'

export default Vue.extend({
  name: 'TodoItem',
  props: {
    value: { type: String, required: true },
    done: { type: Boolean, default: false }
  },
  model: { prop: 'value', event: 'input' },
  methods: {
    onInput(event: Event) {
      this.$emit('input', (event.target as HTMLInputElement).value)
    },
    onToggle() {
      this.$emit('update:done', !this.done)
    }
  },
  render(h) {
    return (
      <li class={{ done: this.done }}>
        <input domPropsValue={this.value} onInput={this.onInput} />
        <BaseButton nativeOnClick={this.onToggle}>toggle</BaseButton>
        {this.$scopedSlots.actions && this.$scopedSlots.actions({ done: this.done })}
      </li>
    )
  }
})
```

Vue 3:

```tsx
import { defineComponent } from 'vue'
import BaseButton from './BaseButton'

export default defineComponent({
  name: 'TodoItem',
  props: {
    modelValue: { type: String, required: true },
    done: { type: Boolean, default: false }
  },
  emits: {
    'update:modelValue': (value: string) => typeof value === 'string',
    'update:done': (value: boolean) => typeof value === 'boolean'
  },
  methods: {
    onInput(event: Event) {
      this.$emit('update:modelValue', (event.target as HTMLInputElement).value)
    },
    onToggle() {
      this.$emit('update:done', !this.done)
    }
  },
  render() {
    return (
      <li class={{ done: this.done }}>
        <input value={this.modelValue} onInput={this.onInput} />
        <BaseButton onClick={this.onToggle}>toggle</BaseButton>
        {this.$slots.actions?.({ done: this.done })}
      </li>
    )
  }
})
```

Changes in this example: `Vue.extend` became `defineComponent`; the `model`
option is gone and `value` became `modelValue`; the `input` event became
`update:modelValue`; `emits` is declared; `domPropsValue` became `value`;
`nativeOnClick` became `onClick`; `$scopedSlots` became `$slots`; the `h`
parameter was dropped.

Callers of this component must change too: `<TodoItem v-model={text} />` keeps
working in Vue 3 JSX, but any caller that passed `value` or listened to `input`
explicitly must now use `modelValue` and `onUpdate:modelValue`. Search for every
usage of each migrated component, not only its definition.

## Slots

All slots are functions in Vue 3, whether or not they receive parameters.

Defining slot content when rendering a child (parent side):

```tsx
import { defineComponent } from 'vue'
import DataList from './DataList'

export default defineComponent({
  name: 'UserPage',
  render() {
    const slots = {
      header: () => <h2>Users</h2>,
      item: (scope: { name: string }) => <li>{scope.name}</li>
    }
    return <DataList v-slots={slots} />
  }
})
```

Reading slots inside a component (child side): `this.$slots.header?.()`. Call
every slot as a function and guard with `?.`, because a slot the parent did not
pass is `undefined`. Vue 2 code that read `this.$slots.default` as an array of
vnodes must now call it: `this.$slots.default?.()`.

## v-model and .sync

- Default `v-model` on a component uses prop `modelValue` and event
  `update:modelValue`. The `model` option no longer exists.
- Vue 2 `.sync` becomes a named `v-model`: `foo.sync` becomes
  `v-model:foo={value}`, with the child emitting `update:foo`.
- Modifiers in JSX use an underscore instead of a dot:
  `v-model:title_trim={this.title}`.
- `v-model` on a native `<input>` in JSX still works: `<input v-model={this.text} />`.

## Events, emits and .native

- Declare every event a component emits in the `emits` option. A listener for an
  undeclared event is treated as a native listener and falls through to the root
  element, which can fire a handler twice when the child also emits that name.
- `.native` is removed. If the parent wants the native click, the child either
  leaves `click` undeclared (the listener falls through) or declares it and emits
  it.
- `$on`, `$off` and `$once` are removed. Replace an instance event bus
  (`new Vue()` used as a bus) with a small mitt-style emitter module or with a
  Pinia store; ask the user which they prefer.

## Refs

- Template refs bound in JSX with `ref="name"` are read through `this.$refs.name`
  in Options components, as before.
- In a `v-for`-like `.map()` render, bind a function ref instead of `refInFor`:
  `ref={(el) => { this.itemEls[index] = el as HTMLElement }}`.
- `this.$refs.x` on a component now returns the component's public instance.
  Methods are visible on it only if the component is an Options API component or
  calls `expose()` in `setup`.

## Functional components

`functional: true` is removed. A functional component is a plain function that
receives `(props, { slots, attrs, emit })`:

```tsx
import type { SetupContext } from 'vue'

interface BadgeProps {
  label: string
}

export function Badge(props: BadgeProps, { slots }: SetupContext) {
  return (
    <span class="badge">
      {props.label}
      {slots.default?.()}
    </span>
  )
}

Badge.props = ['label']
```

Declare `Badge.props` (or `Badge.props = { label: String }`) when the function
should treat `label` as a prop; without it every attribute lands in `attrs`.

## Attributes and listeners

- `this.$attrs` now also contains `class`, `style` and `onXxx` listeners, and
  `$listeners` is gone.
- Components with a single root element inherit these automatically. When a
  component forwards attributes to an inner element, set `inheritAttrs: false`
  and spread them explicitly: `<input {...this.$attrs} />`.
- Components with several roots (fragments) must spread `$attrs` themselves or
  Vue 3 warns.

## Directives

- `v-show` and custom directives work in JSX. Write them camelCased or
  kebab-cased: `vShow={this.visible}` or `v-show={this.visible}`.
- Compile-time directives (`v-if`, `v-for`) do not exist in JSX. Existing
  ternaries and `.map()` calls need no change.
- Custom directive hooks were renamed in Vue 3 (`bind` to `beforeMount`,
  `inserted` to `mounted`, `update` to `beforeUpdate`, `componentUpdated` to
  `updated`, `unbind` to `unmounted`). Rename them in every directive
  definition.

## TypeScript configuration

In `tsconfig.json`:

```json
{
  "compilerOptions": {
    "jsx": "preserve",
    "jsxImportSource": "vue"
  }
}
```

`jsxImportSource` matters because Vue 3.4 and later no longer register a global
`JSX` namespace; without this option TypeScript reports every JSX element as
having an unknown type. Remove Vue 2 shims such as `declare global { namespace
JSX { ... } }` and the `vue-tsx-support/enable-check` import.

## Detection patterns for the inventory phase

`scripts/scan_tsx.py` implements this table, so run it instead of searching by
hand. The table documents what it looks for and why.

| Pattern | Meaning |
|---------|---------|
| `nativeOn` | removed `.native` listeners |
| `domProps` | renamed DOM properties |
| `scopedSlots` / `\$scopedSlots` | merged into slots |
| `\$listeners` | removed |
| `\$children` | removed |
| `refInFor` | removed |
| `functional: true` | functional component to rewrite |
| `Vue\.extend` | replace with `defineComponent` |
| `render\s*\(\s*h\s*\)` | drop the `h` parameter |
| `model:\s*\{` | removed `model` option |
| `\.sync` | named `v-model` |
| `\$on\(`, `\$off\(`, `\$once\(` | removed event API |
| `vue-tsx-support` | remove dependency |
| `vue-property-decorator`, `vue-class-component` | decorators; ask the user |
| `{this.$slots.x}`, `this.$slots.x.length`, `h('div', this.$slots.x)` | slot used as an array of vnodes; call it |
| `beforeDestroy`, `destroyed` | hooks never called in Vue 3 |
| `new Vue()` | probably an event bus; ask the user |
| `tsconfig.json` with `jsx` but no `jsxImportSource` | JSX types missing on Vue 3.4+ |
| `vue-tsx-support`, `@vue/babel-preset-jsx` and similar in `package.json` | removed tooling |
