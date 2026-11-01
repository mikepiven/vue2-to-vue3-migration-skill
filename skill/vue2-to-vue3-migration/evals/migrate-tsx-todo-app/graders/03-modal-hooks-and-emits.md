---
type: llm
focus: trace
weight: 1
---

Modal.tsx uses beforeUnmount instead of beforeDestroy, declares emits including update:visible, and forwards $attrs instead of $listeners.
