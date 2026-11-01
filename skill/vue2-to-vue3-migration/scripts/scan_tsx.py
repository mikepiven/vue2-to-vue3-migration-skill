#!/usr/bin/env python3
"""Scan a project for Vue 2 TSX/JSX patterns that break on Vue 3.

Usage:
    python scan_tsx.py <project-dir> [--format text|json] [--fail-on error|warning|info|none]

The scanner reads .tsx, .jsx, .ts and .js files, package.json and tsconfig*.json.
It uses only the Python standard library. Every finding points to the section of
the skill references that explains the fix.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
EXCLUDED_DIRS = {"node_modules", ".git", "dist", ".nuxt", ".output", "coverage"}
CODE_EXTENSIONS = {".tsx", ".jsx", ".ts", ".js"}

TSX_DOC = "references/tsx-jsx.md"
OPTIONS_DOC = "references/options-to-composition-tsx.md"


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    pattern: "re.Pattern[str]"
    message: str
    reference: str


def _rule(rule_id: str, severity: str, pattern: str, message: str, reference: str) -> Rule:
    return Rule(rule_id, severity, re.compile(pattern), message, reference)


RULES: list[Rule] = [
    _rule(
        "native-on",
        "error",
        r"\bnativeOn(?:[A-Z]\w*)?\b",
        "nativeOn listeners were removed; use onXxx, which falls through to the root element",
        f"{TSX_DOC}#events-emits-and-native",
    ),
    _rule(
        "dom-props",
        "error",
        r"\bdomProps\w*",
        "domProps prefixes are not understood by Vue 3 and render as plain attributes; use the property name directly",
        f"{TSX_DOC}#vnode-format-nested-data-object-becomes-flat-props",
    ),
    _rule(
        "scoped-slots",
        "error",
        r"\bscopedSlots\b",
        "scopedSlots was merged into slots; use v-slots when rendering and this.$slots.name?.() when reading",
        f"{TSX_DOC}#slots",
    ),
    _rule(
        "slots-not-called",
        "warning",
        r"\{\s*(?:this\.)?\$slots\.\w+\s*\}"
        r"|\$slots\.\w+\.(?:length|map|filter|forEach|some|every|find|concat)\b"
        r"|\.\.\.\s*(?:this\.)?\$slots\.\w+\b"
        r"|,\s*(?:this\.)?\$slots\.\w+\s*\)",
        "slot used as an array of vnodes; in Vue 3 every slot is a function, call it with this.$slots.name?.()",
        f"{TSX_DOC}#slots",
    ),
    _rule(
        "listeners",
        "error",
        r"\$listeners\b",
        "$listeners was removed; listeners are part of $attrs",
        f"{TSX_DOC}#attributes-and-listeners",
    ),
    _rule(
        "children",
        "error",
        r"\$children\b",
        "$children was removed; use refs or provide/inject",
        f"{TSX_DOC}#mapping-table",
    ),
    _rule(
        "ref-in-for",
        "error",
        r"\brefInFor\b",
        "refInFor was removed; bind a function ref",
        f"{TSX_DOC}#refs",
    ),
    _rule(
        "functional",
        "error",
        r"\bfunctional\s*:\s*true\b",
        "functional: true was removed; rewrite as a plain function (props, { slots, attrs, emit })",
        f"{TSX_DOC}#functional-components",
    ),
    _rule(
        "vue-extend",
        "error",
        r"\bVue\.extend\s*\(",
        "Vue.extend was removed; use defineComponent from vue",
        f"{TSX_DOC}#mapping-table",
    ),
    _rule(
        "render-h",
        "error",
        r"\brender\s*\(\s*h\s*[,)]",
        "render no longer receives h; drop the parameter or import h from vue",
        f"{TSX_DOC}#mapping-table",
    ),
    _rule(
        "model-option",
        "warning",
        r"^\s*model\s*:\s*\{",
        "the model component option was removed; use modelValue and update:modelValue",
        f"{TSX_DOC}#v-model-and-sync",
    ),
    _rule(
        "sync-modifier",
        "warning",
        r"\w\.sync\s*=\s*[{\"']",
        ".sync was replaced by a named v-model, v-model:foo",
        f"{TSX_DOC}#v-model-and-sync",
    ),
    _rule(
        "event-api",
        "error",
        r"\.\$(?:on|off|once)\s*\(",
        "$on, $off and $once were removed from component instances",
        f"{TSX_DOC}#events-emits-and-native",
    ),
    _rule(
        "new-vue-bus",
        "warning",
        r"\bnew\s+Vue\s*\(\s*\)",
        "a bare Vue instance is usually an event bus, which no longer works; replace it with an emitter or a store (ask the user)",
        f"{TSX_DOC}#events-emits-and-native",
    ),
    _rule(
        "vue-set",
        "info",
        r"\bVue\.(?:set|delete)\s*\(|\.\$(?:set|delete)\s*\(",
        "Vue.set and Vue.delete are not needed in Vue 3; use plain assignment and delete",
        f"{OPTIONS_DOC}#watchers",
    ),
    _rule(
        "destroy-hooks",
        "error",
        r"^\s*(?:beforeDestroy|destroyed)\s*(?:\(|:)",
        "beforeDestroy and destroyed are never called in Vue 3; rename to beforeUnmount and unmounted",
        f"{OPTIONS_DOC}#mandatory-renames-that-apply-even-without-conversion",
    ),
    _rule(
        "decorators",
        "error",
        r"from\s+['\"](?:vue-property-decorator|vue-class-component)['\"]",
        "class components with decorators are not covered by this skill; leave the file unchanged and ask the user how to proceed",
        f"{TSX_DOC}#tooling-swap",
    ),
]

REMOVED_DEPENDENCIES = {
    "vue-tsx-support": "remove it and use defineComponent typing",
    "@vue/babel-preset-jsx": "replace with @vue/babel-plugin-jsx or @vitejs/plugin-vue-jsx",
    "@vue/babel-plugin-transform-vue-jsx": "replace with @vue/babel-plugin-jsx or @vitejs/plugin-vue-jsx",
    "@vue/babel-helper-vue-jsx-merge-props": "remove it; Vue 3 JSX plugins do not need a merge helper",
    "babel-helper-vue-jsx-merge-props": "remove it; Vue 3 JSX plugins do not need a merge helper",
    "vue-property-decorator": "class components are not covered; ask the user how to proceed",
    "vue-class-component": "class components are not covered; ask the user how to proceed",
}

DEPENDENCY_SECTIONS = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
VUE_2_SPEC = re.compile(r"^[~^>=\s]*2\.")


def iter_code_lines(text: str) -> Iterator[tuple[int, str]]:
    """Yield (line number, line) for lines that are not comments.

    Only whole-line comments are skipped. Inline trailing comments are kept,
    because stripping them reliably needs a real parser and a wrong guess would
    hide findings.
    """
    in_block = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if in_block:
            if "*/" in stripped:
                in_block = False
            continue
        if stripped.startswith("//"):
            continue
        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_block = True
            continue
        yield number, line


def make_finding(path: str, line: int, column: int, rule: str, severity: str, message: str, reference: str) -> dict:
    return {
        "file": path,
        "line": line,
        "column": column,
        "rule": rule,
        "severity": severity,
        "message": message,
        "reference": reference,
    }


def scan_code(relative: str, text: str) -> list[dict]:
    findings = []
    for number, line in iter_code_lines(text):
        for rule in RULES:
            match = rule.pattern.search(line)
            if match:
                findings.append(
                    make_finding(relative, number, match.start() + 1, rule.id, rule.severity, rule.message, rule.reference)
                )
    return findings


def find_line(text: str, needle: str) -> int:
    for number, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return number
    return 1


def scan_package_json(relative: str, text: str) -> list[dict]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    findings = []
    for section in DEPENDENCY_SECTIONS:
        dependencies = data.get(section) or {}
        if not isinstance(dependencies, dict):
            continue
        for name, spec in dependencies.items():
            if name in REMOVED_DEPENDENCIES:
                findings.append(
                    make_finding(
                        relative,
                        find_line(text, f'"{name}"'),
                        1,
                        "removed-dependency",
                        "error",
                        f"{name}: {REMOVED_DEPENDENCIES[name]}",
                        f"{TSX_DOC}#tooling-swap",
                    )
                )
            if name == "vue" and isinstance(spec, str) and VUE_2_SPEC.match(spec):
                findings.append(
                    make_finding(
                        relative,
                        find_line(text, '"vue"'),
                        1,
                        "vue-2-dependency",
                        "warning",
                        f"vue {spec} is a Vue 2 version; set it from the chosen preset",
                        "references/presets.md#presets",
                    )
                )
    return findings


def scan_tsconfig(relative: str, text: str) -> list[dict]:
    without_comments = "\n".join(line for line in text.splitlines() if not line.strip().startswith("//"))
    try:
        data = json.loads(without_comments)
    except json.JSONDecodeError:
        return []
    options = data.get("compilerOptions") or {}
    if "jsx" in options and options.get("jsxImportSource") != "vue":
        return [
            make_finding(
                relative,
                find_line(text, '"jsx"'),
                1,
                "tsconfig-jsx-import-source",
                "warning",
                'tsconfig sets "jsx" but not "jsxImportSource": "vue"; Vue 3.4+ no longer registers a global JSX namespace',
                f"{TSX_DOC}#typescript-configuration",
            )
        ]
    return []


def scan_file(path: Path, root: Path) -> list[dict]:
    relative = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix in CODE_EXTENSIONS:
        return scan_code(relative, text)
    if path.name == "package.json":
        return scan_package_json(relative, text)
    if path.name.startswith("tsconfig") and path.suffix == ".json":
        return scan_tsconfig(relative, text)
    return []


def iter_files(root: Path) -> Iterator[Path]:
    for current, directories, files in os.walk(root):
        directories[:] = sorted(d for d in directories if d not in EXCLUDED_DIRS)
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix in CODE_EXTENSIONS or name == "package.json" or (
                name.startswith("tsconfig") and path.suffix == ".json"
            ):
                yield path


def scan_project(root: Path) -> list[dict]:
    findings: list[dict] = []
    for path in iter_files(root):
        findings.extend(scan_file(path, root))
    return findings


def summarize(findings: list[dict]) -> dict:
    summary = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        summary[finding["severity"]] += 1
    return summary


def format_text(findings: list[dict]) -> str:
    lines: list[str] = []
    current = None
    for finding in findings:
        if finding["file"] != current:
            current = finding["file"]
            lines.append(current)
        lines.append(
            "  {line}:{column}  {severity}  {rule}  {message} ({reference})".format(**finding)
        )
    summary = summarize(findings)
    lines.append("")
    lines.append(
        "Summary: {error} error(s), {warning} warning(s), {info} info".format(**summary)
    )
    return "\n".join(lines)


def should_fail(findings: list[dict], threshold: str) -> bool:
    if threshold == "none":
        return False
    limit = SEVERITY_ORDER[threshold]
    return any(SEVERITY_ORDER[f["severity"]] >= limit for f in findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a project for Vue 2 TSX/JSX patterns that break on Vue 3.")
    parser.add_argument("path", help="project directory to scan")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("error", "warning", "info", "none"), default="none")
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.is_dir():
        print(f"error: {args.path} is not a directory", file=sys.stderr)
        return 2

    findings = scan_project(root)
    if args.format == "json":
        print(json.dumps({"root": str(root), "findings": findings, "summary": summarize(findings)}, indent=2))
    else:
        print(format_text(findings))
    return 1 if should_fail(findings, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
