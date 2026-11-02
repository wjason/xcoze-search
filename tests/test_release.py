"""Release checks use temporary source fixtures, without network or credentials."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_release.py"
spec = importlib.util.spec_from_file_location("prepare_release", SCRIPT)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "scripts").mkdir()
        for name in ("xcoze_search.py", "build_release.py"):
            (self.root / "scripts" / name).write_text('VERSION = "0.2.0"\n', encoding="utf-8")
        (self.root / "SKILL.md").write_text('---\nname: fixture\nmetadata:\n  version: "0.2.0"\n---\n', encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text(
            '# Changes\n\n## v0.2.0 — 2026-11-02\n\nCurrent release.\n\n## v0.1.0 — 2026-10-24\n\nOld release.\n', encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def test_extracts_only_matching_release_notes(self):
        notes = release.prepare_notes(self.root, "v0.2.0")
        self.assertIn("Current release.", notes)
        self.assertNotIn("Old release.", notes)

    def test_refuses_mismatched_tag_or_component_version(self):
        with self.assertRaises(ValueError):
            release.prepare_notes(self.root, "v0.3.0")
        for path in ("scripts/xcoze_search.py", "scripts/build_release.py", "SKILL.md"):
            file = self.root / path
            before = file.read_text(encoding="utf-8")
            file.write_text(before.replace("0.2.0", "0.1.0"), encoding="utf-8")
            with self.subTest(path=path), self.assertRaises(ValueError):
                release.prepare_notes(self.root, "v0.2.0")
            file.write_text(before, encoding="utf-8")

    def test_refuses_missing_or_empty_release_notes(self):
        for changelog in ("## Unreleased\n", "## v0.2.0 — 2026-11-02\n\n## v0.1.0 — 2026-10-24\nOld."):
            (self.root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
            with self.assertRaises(ValueError):
                release.prepare_notes(self.root, "v0.2.0")

    def test_language_selection_defaults_to_chinese_and_checks_english_version(self):
        (self.root / "CHANGELOG.md").write_text('## v0.2.0 — 2026-11-02\n\n中文说明。\n', encoding="utf-8")
        english = self.root / "CHANGELOG.en.md"
        english.write_text('## v0.2.0 — 2026-11-02\n\nEnglish notes.\n', encoding="utf-8")
        default = release.prepare_notes(self.root, "v0.2.0")
        self.assertIn("中文说明", default)
        self.assertNotIn("English notes", default)
        self.assertIn("English notes", release.prepare_notes(self.root, "v0.2.0", "en"))
        both = release.prepare_notes(self.root, "v0.2.0", "both")
        self.assertLess(both.index("中文说明"), both.index("<details>"))
        self.assertIn("<summary>English</summary>", both)
        self.assertIn("English notes", both)
        english.write_text('## v0.1.0 — 2026-10-24\n\nOutdated.\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            release.prepare_notes(self.root, "v0.2.0", "both")


if __name__ == "__main__":
    unittest.main()
