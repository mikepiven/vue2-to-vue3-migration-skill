---
tags: [vue2-to-vue3-migration]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I've got a small Vue 2.7 app written in TSX in the current directory (components in src/components, entry in src/App.tsx). We're moving to Vue 3 with the stable preset and I want to keep the Options API for now, no Composition API rewrite yet. Please migrate everything you can, and tell me clearly about anything you couldn't or shouldn't do on your own.

Input files: package.json, tsconfig.json, src/App.tsx, src/bus.ts, src/components/BaseButton.tsx, src/components/TodoItem.tsx, src/components/Badge.tsx, src/components/DataList.tsx, src/components/Modal.tsx, src/components/LegacyWidget.tsx
