"""Tests for skill/vue2-to-vue3-migration/scripts/scan_tsx.py (standard library only)."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skill" / "vue2-to-vue3-migration"
SCRIPT = SKILL / "scripts" / "scan_tsx.py"
INPUT_FIXTURE = SKILL / "evals" / "migrate-tsx-todo-app" / "files"
EXPECTED_FIXTURE = REPO / "tests" / "fixtures" / "expected-vue3"

_spec = importlib.util.spec_from_file_location("scan_tsx", SCRIPT)
scan_tsx = importlib.util.module_from_spec(_spec)
sys.modules["scan_tsx"] = scan_tsx
_spec.loader.exec_module(scan_tsx)

# rule id -> (snippet or snippets that must match, snippets that must not match)
RULE_CASES: dict[str, tuple[str | list[str], list[str]]] = {
    "native-on": ("<A nativeOnClick={f} />", ["<A onClick={f} />", "const nativeOnly = 1"]),
    "dom-props": ("<div domPropsInnerHTML={html} />", ["const domain = 1"]),
    "scoped-slots": ("this.$scopedSlots.item({})", ["this.$slots.item?.({})"]),
    "slots-not-called": (
        [
            "{this.$slots.default}",
            "{ this.$slots.default }",
            "this.$slots.default.length",
            "h('div', this.$slots.default)",
            "const all = [...this.$slots.default]",
        ],
        [
            "{this.$slots.default?.()}",
            "this.$slots.default()",
            "this.$slots.footer?.({ a: 1 })",
            "{this.$slots.item ? this.$slots.item({}) : null}",
            "if (!this.$slots.default) { return null }",
            "return this.$slots.header && this.$slots.header()",
        ],
    ),
    "listeners": ("{...{ on: this.$listeners }}", ["const listeners = []"]),
    "children": ("this.$children.length", ["const children = []"]),
    "ref-in-for": ("<li refInFor={true} />", ['<li ref="x" />']),
    "functional": ("  functional: true,", ["  functional: false,"]),
    "vue-extend": ("export default Vue.extend({", ["export default defineComponent({"]),
    "render-h": ("  render(h) {", ["  render() {", "  render(handler) {"]),
    "model-option": (
        "  model: { prop: 'value', event: 'input' },",
        ["  modelValue: { type: String },"],
    ),
    "sync-modifier": ("<Foo title.sync={title} />", ["const files = glob.sync('*.ts')"]),
    "event-api": ("bus.$on('x', fn)", ["this.$emit('x')", "const onClick = 1"]),
    "new-vue-bus": ("export const bus = new Vue()", ["const app = createApp(App)"]),
    "vue-set": ("Vue.set(obj, 'a', 1)", ["obj.a = 1"]),
    "destroy-hooks": ("  beforeDestroy() {", ["  beforeUnmount() {"]),
    "decorators": (
        "import { Component } from 'vue-property-decorator'",
        ["import { defineComponent } from 'vue'"],
    ),
}

# file (relative to the input fixture) -> exact set of rule ids expected
INPUT_EXPECTATIONS: dict[str, set[str]] = {
    "src/App.tsx": {"vue-extend", "render-h", "scoped-slots", "native-on"},
    "src/bus.ts": {"new-vue-bus"},
    "src/components/BaseButton.tsx": {"vue-extend", "render-h", "slots-not-called"},
    "src/components/Badge.tsx": {"vue-extend", "functional", "render-h"},
    "src/components/DataList.tsx": {"vue-extend", "render-h", "scoped-slots", "ref-in-for"},
    "src/components/Modal.tsx": {
        "vue-extend",
        "render-h",
        "native-on",
        "listeners",
        "event-api",
        "destroy-hooks",
        "slots-not-called",
    },
    "src/components/TodoItem.tsx": {
        "vue-extend",
        "render-h",
        "model-option",
        "dom-props",
        "native-on",
        "scoped-slots",
    },
    "src/components/LegacyWidget.tsx": {"decorators"},
    "package.json": {"removed-dependency", "vue-2-dependency"},
    "tsconfig.json": {"tsconfig-jsx-import-source"},
}


def github_slug(heading: str) -> str:
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s", "-", slug)


def headings(markdown_path: Path) -> set[str]:
    found = set()
    for line in markdown_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.*)$", line)
        if match:
            found.add(github_slug(match.group(1)))
    return found


class ScanSnippet(unittest.TestCase):
    def scan(self, filename: str, content: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return scan_tsx.scan_project(root)

    def rule_ids(self, filename: str, content: str) -> set[str]:
        return {f["rule"] for f in self.scan(filename, content)}


class RuleTests(ScanSnippet):
    def test_every_code_rule_has_a_case(self):
        self.assertEqual({r.id for r in scan_tsx.RULES}, set(RULE_CASES))

    def test_rules_match_positive_snippets(self):
        for rule_id, (positives, _) in RULE_CASES.items():
            snippets = [positives] if isinstance(positives, str) else positives
            for snippet in snippets:
                with self.subTest(rule=rule_id, snippet=snippet):
                    self.assertIn(rule_id, self.rule_ids("a.tsx", snippet + "\n"))

    def test_rules_ignore_negative_snippets(self):
        for rule_id, (_, negatives) in RULE_CASES.items():
            for negative in negatives:
                with self.subTest(rule=rule_id, snippet=negative):
                    self.assertNotIn(rule_id, self.rule_ids("a.tsx", negative + "\n"))

    def test_reports_line_and_column(self):
        findings = self.scan("a.tsx", "const a = 1\n  nativeOnClick={f}\n")
        self.assertEqual(len(findings), 1)
        self.assertEqual((findings[0]["line"], findings[0]["column"]), (2, 3))
        self.assertEqual(findings[0]["file"], "a.tsx")


class CommentTests(ScanSnippet):
    def test_line_comments_are_ignored(self):
        self.assertEqual(self.rule_ids("a.tsx", "// nativeOnClick={f}\n"), set())

    def test_block_comments_are_ignored(self):
        content = "/*\n * Vue.extend({\n * render(h) {\n */\nconst a = 1\n"
        self.assertEqual(self.rule_ids("a.tsx", content), set())

    def test_code_after_a_block_comment_is_scanned(self):
        content = "/* note */\nexport default Vue.extend({\n"
        self.assertEqual(self.rule_ids("a.tsx", content), {"vue-extend"})


class ProjectWalkTests(ScanSnippet):
    def test_excluded_directories_are_skipped(self):
        for directory in ("node_modules", "dist", ".nuxt", ".output", ".git"):
            with self.subTest(directory=directory):
                self.assertEqual(
                    self.rule_ids(f"{directory}/pkg/a.tsx", "export default Vue.extend({\n"), set()
                )

    def test_non_code_files_are_ignored(self):
        self.assertEqual(self.rule_ids("notes.md", "Vue.extend({\n"), set())

    def test_all_code_extensions_are_scanned(self):
        for extension in ("tsx", "jsx", "ts", "js"):
            with self.subTest(extension=extension):
                self.assertEqual(
                    self.rule_ids(f"a.{extension}", "export default Vue.extend({\n"), {"vue-extend"}
                )


class PackageJsonTests(ScanSnippet):
    def test_flags_removed_dependencies_in_every_section(self):
        content = json.dumps(
            {
                "dependencies": {"vue-tsx-support": "^3.2.0"},
                "devDependencies": {"@vue/babel-preset-jsx": "^1.4.0"},
                "peerDependencies": {"vue-class-component": "^7.2.6"},
            }
        )
        findings = [f for f in self.scan("package.json", content) if f["rule"] == "removed-dependency"]
        self.assertEqual(len(findings), 3)

    def test_flags_vue_2_versions_only(self):
        for spec in ("2.7.16", "^2.7.16", "~2.6.0", ">=2.6"):
            with self.subTest(spec=spec):
                ids = self.rule_ids("package.json", json.dumps({"dependencies": {"vue": spec}}))
                self.assertIn("vue-2-dependency", ids)
        for spec in ("^3.5.0", "3.4.0", "latest"):
            with self.subTest(spec=spec):
                ids = self.rule_ids("package.json", json.dumps({"dependencies": {"vue": spec}}))
                self.assertNotIn("vue-2-dependency", ids)

    def test_invalid_json_does_not_crash(self):
        self.assertEqual(self.rule_ids("package.json", "{ not json"), set())

    def test_line_number_points_at_the_dependency(self):
        content = '{\n  "dependencies": {\n    "vue-tsx-support": "^3.2.0"\n  }\n}\n'
        findings = self.scan("package.json", content)
        self.assertEqual(findings[0]["line"], 3)


class TsconfigTests(ScanSnippet):
    def test_flags_missing_jsx_import_source(self):
        content = json.dumps({"compilerOptions": {"jsx": "preserve"}})
        self.assertEqual(self.rule_ids("tsconfig.json", content), {"tsconfig-jsx-import-source"})

    def test_accepts_vue_jsx_import_source(self):
        content = json.dumps({"compilerOptions": {"jsx": "preserve", "jsxImportSource": "vue"}})
        self.assertEqual(self.rule_ids("tsconfig.json", content), set())

    def test_ignores_projects_without_jsx(self):
        content = json.dumps({"compilerOptions": {"strict": True}})
        self.assertEqual(self.rule_ids("tsconfig.json", content), set())

    def test_tolerates_comment_lines(self):
        content = '{\n  // a comment\n  "compilerOptions": { "jsx": "preserve" }\n}\n'
        self.assertEqual(self.rule_ids("tsconfig.json", content), {"tsconfig-jsx-import-source"})

    def test_matches_tsconfig_variants(self):
        content = json.dumps({"compilerOptions": {"jsx": "preserve"}})
        self.assertEqual(self.rule_ids("tsconfig.app.json", content), {"tsconfig-jsx-import-source"})


class FixtureTests(unittest.TestCase):
    def test_input_fixture_findings_per_file(self):
        findings = scan_tsx.scan_project(INPUT_FIXTURE)
        by_file: dict[str, set[str]] = {}
        for finding in findings:
            by_file.setdefault(finding["file"], set()).add(finding["rule"])
        self.assertEqual(by_file, INPUT_EXPECTATIONS)

    def test_input_fixture_removed_dependency_count(self):
        findings = scan_tsx.scan_project(INPUT_FIXTURE)
        removed = [f for f in findings if f["rule"] == "removed-dependency"]
        self.assertEqual(len(removed), 4)

    def test_expected_vue3_result_has_no_findings(self):
        self.assertEqual(scan_tsx.scan_project(EXPECTED_FIXTURE), [])

    def test_expected_result_covers_every_migrated_input_file(self):
        input_files = {p.relative_to(INPUT_FIXTURE) for p in INPUT_FIXTURE.rglob("*") if p.is_file()}
        expected_files = {p.relative_to(EXPECTED_FIXTURE) for p in EXPECTED_FIXTURE.rglob("*") if p.is_file()}
        expected_files.discard(Path("README.md"))
        missing = input_files - expected_files
        self.assertEqual(missing, {Path("src/components/LegacyWidget.tsx")})


class ReferenceConsistencyTests(unittest.TestCase):
    def test_every_rule_points_at_an_existing_heading(self):
        references = [rule.reference for rule in scan_tsx.RULES]
        references += [
            "references/tsx-jsx.md#tooling-swap",
            "references/presets.md#presets",
            "references/tsx-jsx.md#typescript-configuration",
        ]
        for reference in references:
            with self.subTest(reference=reference):
                path, anchor = reference.split("#")
                self.assertTrue((SKILL / path).is_file(), f"{path} does not exist")
                self.assertIn(anchor, headings(SKILL / path))


class CliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments], capture_output=True, text=True, check=False
        )

    def test_json_output_shape(self):
        result = self.run_cli(str(INPUT_FIXTURE), "--format", "json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"root", "findings", "summary"})
        self.assertEqual(
            set(payload["findings"][0]),
            {"file", "line", "column", "rule", "severity", "message", "reference"},
        )
        self.assertEqual(sum(payload["summary"].values()), len(payload["findings"]))

    def test_text_output_ends_with_summary(self):
        result = self.run_cli(str(INPUT_FIXTURE))
        self.assertEqual(result.returncode, 0)
        self.assertRegex(result.stdout.strip().splitlines()[-1], r"^Summary: \d+ error\(s\)")

    def test_fail_on_error_exits_one_on_the_input_fixture(self):
        self.assertEqual(self.run_cli(str(INPUT_FIXTURE), "--fail-on", "error").returncode, 1)

    def test_fail_on_error_exits_zero_on_the_expected_result(self):
        self.assertEqual(self.run_cli(str(EXPECTED_FIXTURE), "--fail-on", "info").returncode, 0)

    def test_missing_directory_exits_two(self):
        result = self.run_cli(str(REPO / "does-not-exist"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a directory", result.stderr)

    def test_should_fail_threshold_ordering(self):
        warning_only = [{"severity": "warning"}]
        self.assertFalse(scan_tsx.should_fail(warning_only, "error"))
        self.assertTrue(scan_tsx.should_fail(warning_only, "warning"))
        self.assertTrue(scan_tsx.should_fail(warning_only, "info"))
        self.assertFalse(scan_tsx.should_fail(warning_only, "none"))


if __name__ == "__main__":
    unittest.main()
