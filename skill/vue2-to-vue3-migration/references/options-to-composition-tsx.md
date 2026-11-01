# Options API to Composition API for TSX components

Read this file after the component already runs on Vue 3 (see `tsx-jsx.md`) and
the user wants Composition API. Conversion is optional: Vue 3 keeps the Options
API, and a component that works as Options can stay that way. Convert only when
the user asked for it, and convert one component per commit so that a
regression points at one file.

## Contents

- Mandatory renames that apply even without conversion
- Mapping table
- Complete before and after example
- Props: do not destructure
- Watchers
- Lifecycle
- Template refs and exposing methods
- Mixins become composables
- Checklist per component

## Mandatory renames that apply even without conversion

Vue 3 never calls the Vue 2 destroy hooks, so a component that keeps them
silently skips its cleanup code.

| Vue 2 | Vue 3 |
|-------|-------|
| `beforeDestroy` | `beforeUnmount` |
| `destroyed` | `unmounted` |

Rename them in every Options component, converted or not.

## Mapping table

| Options API | Composition API in `setup` |
|-------------|----------------------------|
| `data() { return { n: 0 } }` | `const n = ref(0)` (or `reactive({ ... })` for an object of related fields) |
| `computed: { total() { ... } }` | `const total = computed(() => ...)` |
| `methods: { go() { ... } }` | `const go = () => { ... }` |
| `watch: { n(v) { ... } }` | `watch(n, (v) => { ... })` |
| `created()` | code at the top level of `setup` |
| `mounted()` | `onMounted(() => { ... })` |
| `beforeUpdate()` / `updated()` | `onBeforeUpdate` / `onUpdated` |
| `beforeUnmount()` / `unmounted()` | `onBeforeUnmount` / `onUnmounted` |
| `this.$emit('x', v)` | `emit('x', v)` from the setup context |
| `this.$slots` | `slots` from the setup context |
| `this.$attrs` | `attrs` from the setup context |
| `this.$refs.el` | a `ref()` bound with `ref={el}` in the returned render function |
| `this.$route`, `this.$router` | `useRoute()`, `useRouter()` |
| `this.$store` | the Pinia store composable (handled in the Pinia step) |
| `provide() { ... }` / `inject: [...]` | `provide(key, value)` / `inject(key)` |
| `mixins: [m]` | a composable function (see below) |
| `render() { ... }` | `setup` returns `() => ( ... )` |

`setup` has no `this`. Every `this.x` must become a local variable, a prop read
through `props`, or a context member.

## Complete before and after example

Options API (already working on Vue 3):

```tsx
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'SearchBox',
  props: {
    placeholder: { type: String, default: 'Search' },
    debounceMs: { type: Number, default: 300 }
  },
  emits: {
    search: (query: string) => typeof query === 'string'
  },
  data() {
    return {
      query: '',
      timer: null as ReturnType<typeof setTimeout> | null
    }
  },
  computed: {
    isEmpty(): boolean {
      return this.query.trim().length === 0
    }
  },
  watch: {
    query(value: string) {
      if (this.timer) {
        clearTimeout(this.timer)
      }
      this.timer = setTimeout(() => {
        this.$emit('search', value)
      }, this.debounceMs)
    }
  },
  mounted() {
    (this.$refs.input as HTMLInputElement).focus()
  },
  beforeUnmount() {
    if (this.timer) {
      clearTimeout(this.timer)
    }
  },
  methods: {
    clear() {
      this.query = ''
    },
    onInput(event: Event) {
      this.query = (event.target as HTMLInputElement).value
    }
  },
  render() {
    return (
      <div class="search-box">
        <input
          ref="input"
          value={this.query}
          placeholder={this.placeholder}
          onInput={this.onInput}
        />
        {!this.isEmpty && <button onClick={this.clear}>x</button>}
      </div>
    )
  }
})
```

Composition API:

```tsx
import {
  computed,
  defineComponent,
  onBeforeUnmount,
  onMounted,
  ref,
  watch
} from 'vue'

export default defineComponent({
  name: 'SearchBox',
  props: {
    placeholder: { type: String, default: 'Search' },
    debounceMs: { type: Number, default: 300 }
  },
  emits: {
    search: (query: string) => typeof query === 'string'
  },
  setup(props, { emit }) {
    const query = ref('')
    const inputEl = ref<HTMLInputElement | null>(null)
    let timer: ReturnType<typeof setTimeout> | null = null

    const isEmpty = computed(() => query.value.trim().length === 0)

    watch(query, (value) => {
      if (timer) {
        clearTimeout(timer)
      }
      timer = setTimeout(() => {
        emit('search', value)
      }, props.debounceMs)
    })

    onMounted(() => {
      inputEl.value?.focus()
    })

    onBeforeUnmount(() => {
      if (timer) {
        clearTimeout(timer)
      }
    })

    const clear = () => {
      query.value = ''
    }

    const onInput = (event: Event) => {
      query.value = (event.target as HTMLInputElement).value
    }

    return () => (
      <div class="search-box">
        <input
          ref={inputEl}
          value={query.value}
          placeholder={props.placeholder}
          onInput={onInput}
        />
        {!isEmpty.value && <button onClick={clear}>x</button>}
      </div>
    )
  }
})
```

Points to notice in the conversion:

- `timer` was reactive data in the Options version although nothing renders
  from it. In `setup` it becomes a plain `let`, which avoids needless reactivity.
- `.value` is required in script code (`query.value`) and also inside the
  returned render function (`query.value`, `isEmpty.value`). Forgetting it in
  JSX renders `[object Object]` or a stale value without any error.
- `setup` returns a function. That function is the render function and is
  re-run when any ref it reads changes.
- The `emits` declaration stays; `emit` comes from the context instead of
  `this.$emit`.

## Props: do not destructure

Reading `props.placeholder` inside the render function or a watcher getter
keeps reactivity. Destructuring `const { placeholder } = props` in `setup` copies
the value once and loses updates.

The Vue 3.5 reactive props destructure is a compile-time feature of
`<script setup>`. TSX components go through the JSX transform, which does not
apply it, so never rely on it here. Use `props.x` directly, or
`toRef(props, 'x')` / `toRefs(props)` when a ref is needed.

## Watchers

- To watch a prop, pass a getter: `watch(() => props.value, (v) => { ... })`.
  `watch(props.value, ...)` watches a constant.
- In Vue 3, a watcher on an array fires on replacement only. Mutations such as
  `push` trigger it only with `{ deep: true }`. Check every Vue 2 watcher whose
  source is an array and add `deep: true` where mutation was relied on.
- `immediate: true` carries over as the third argument:
  `watch(source, cb, { immediate: true })`.
- `Vue.set` and `Vue.delete` are not needed: Vue 3 tracks added and removed
  properties on reactive objects. Replace them with plain assignment and
  `delete`.

## Lifecycle

Code that lived in `created` runs at the top level of `setup`. Code that needs
the DOM goes into `onMounted`. Register cleanup in `onBeforeUnmount` or
`onUnmounted`: timers, event listeners on `window`, observers, and
subscriptions.

## Template refs and exposing methods

Bind a ref created in `setup` with `ref={el}` in the returned render function,
as in the example. A ref that is `null` before mount must be typed as
`ref<HTMLInputElement | null>(null)`.

When `setup` returns a render function, nothing declared in `setup` is visible
to a parent that holds a ref to this component. If the parent calls a method
such as `searchBox.value?.focus()`, expose it:

```tsx
setup(props, { expose }) {
  const inputEl = ref<HTMLInputElement | null>(null)

  const focus = () => {
    inputEl.value?.focus()
  }

  expose({ focus })

  return () => <input ref={inputEl} />
}
```

Search the project for parents that call methods through `$refs` before
converting a child, because an Options component exposes its methods
automatically and a converted one does not.

## Mixins become composables

A mixin shares state and hooks through merging, which hides where a name comes
from. A composable is a function that returns what it provides.

Mixin:

```ts
export const windowWidthMixin = {
  data() {
    return { windowWidth: window.innerWidth }
  },
  mounted() {
    window.addEventListener('resize', this.onResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.onResize)
  },
  methods: {
    onResize() {
      this.windowWidth = window.innerWidth
    }
  }
}
```

Composable:

```ts
import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useWindowWidth() {
  const windowWidth = ref(window.innerWidth)

  const onResize = () => {
    windowWidth.value = window.innerWidth
  }

  onMounted(() => {
    window.addEventListener('resize', onResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', onResize)
  })

  return { windowWidth }
}
```

Usage in a component: `const { windowWidth } = useWindowWidth()`. Convert a
mixin only after every component that uses it is ready to convert, or keep the
mixin until the last user is migrated: Options components can still use mixins
in Vue 3.

## Checklist per component

1. Hooks renamed (`beforeUnmount`, `unmounted`).
2. Every `this.` is gone from `setup` and from the returned render function.
3. Every ref read in JSX has `.value`.
4. Props are read through `props`, not destructured.
5. Array watchers have `deep: true` where mutation mattered.
6. Methods that parents call through `$refs` are passed to `expose`.
7. `emits` is declared and matches every `emit` call.
8. The component builds, type-checks, and its tests pass.
