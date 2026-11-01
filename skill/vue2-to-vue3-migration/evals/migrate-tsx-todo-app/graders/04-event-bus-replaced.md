---
type: llm
focus: trace
weight: 1
---

src/bus.ts no longer creates a Vue instance, and no code calls $on or $off on one; either a plain emitter replaces it or the final message asks the user which replacement they prefer.
