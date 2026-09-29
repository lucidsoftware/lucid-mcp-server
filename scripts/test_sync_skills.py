"""Behavioral tests for skill sync and optional plugin version bumps."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sync_skills


class SkillSyncVersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        root_patch = patch.object(sync_skills, "REPO_ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def target(self, name, skills=("lucid",), version="1.2.3"):
        manifest = self.write(
            f"{name}/plugin.json", f'{{\n  "name": "{name}",\n  "version": "{version}"\n}}\n'
        )
        return sync_skills.Target(self.root / name / "skills", list(skills), manifest)

    def run_sync(self, targets, **options):
        settings = dict(
            check=False,
            dry_run=False,
            prune=False,
            bump_version=True,
            only_targets=None,
            only_skills=None,
            verbose=False,
        )
        settings.update(options)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = sync_skills.run(
                sync_skills.Config(self.root / "skills", targets), **settings
            )
        return result, output.getvalue()

    def test_existing_skill_bumps_patch_once_and_preserves_manifest_content(self):
        self.write("skills/lucid/SKILL.md", "updated")
        self.write("plugin/skills/lucid/SKILL.md", "old")
        target = self.target("plugin")
        original = target.manifest.read_text().replace('"name": "plugin"', '"name": "plugin",\n  "custom": true')
        target.manifest.write_text(original)

        result, _ = self.run_sync([target])
        self.assertEqual(result, 0)
        self.assertEqual((self.root / "plugin/skills/lucid/SKILL.md").read_text(), "updated")
        self.assertEqual(target.manifest.read_text(), original.replace("1.2.3", "1.2.4"))

        result, output = self.run_sync([target])
        self.assertEqual(result, 0)
        self.assertNotIn("[version]", output)
        self.assertIn('"version": "1.2.4"', target.manifest.read_text())

    def test_new_skill_bumps_minor_per_target_and_wins_over_patch(self):
        self.write("skills/lucid/SKILL.md", "updated")
        self.write("skills/new-skill/SKILL.md", "new")
        self.write("first/skills/lucid/SKILL.md", "old")
        self.write("second/skills/lucid/SKILL.md", "updated")
        first = self.target("first", ("lucid", "new-skill"))
        second = self.target("second", ("lucid", "new-skill"))

        result, output = self.run_sync([first, second])
        self.assertEqual(result, 0)
        self.assertEqual(output.count("[version]"), 2)
        self.assertIn('"version": "1.3.0"', first.manifest.read_text())
        self.assertIn('"version": "1.3.0"', second.manifest.read_text())

    def test_dry_run_previews_without_writing_and_filter_keeps_other_skills(self):
        self.write("skills/new-skill/SKILL.md", "new")
        existing = self.write("plugin/skills/lucid/SKILL.md", "keep")
        target = self.target("plugin", ("lucid", "new-skill"))

        result, output = self.run_sync(
            [target], dry_run=True, only_skills=["new-skill"], prune=True
        )
        self.assertEqual(result, 0)
        self.assertIn("1.2.3 -> 1.3.0 (dry run)", output)
        self.assertNotIn("stale skill", output)
        self.assertEqual(existing.read_text(), "keep")
        self.assertFalse((self.root / "plugin/skills/new-skill").exists())
        self.assertIn('"version": "1.2.3"', target.manifest.read_text())

    def test_prune_bumps_patch_once(self):
        self.write("plugin/skills/removed/SKILL.md", "old")
        target = self.target("plugin", ())

        result, output = self.run_sync([target], prune=True)
        self.assertEqual(result, 0)
        self.assertIn("[prune] removed", output)
        self.assertFalse((self.root / "plugin/skills/removed").exists())
        self.assertIn('"version": "1.2.4"', target.manifest.read_text())

    def test_target_filter_only_changes_selected_plugin(self):
        self.write("skills/lucid/SKILL.md", "updated")
        first_copy = self.write("first/skills/lucid/SKILL.md", "old")
        second_copy = self.write("second/skills/lucid/SKILL.md", "old")
        first = self.target("first")
        second = self.target("second")

        result, output = self.run_sync(
            [first, second], only_targets=["first/skills"]
        )
        self.assertEqual(result, 0)
        self.assertEqual(output.count("[version]"), 1)
        self.assertEqual(first_copy.read_text(), "updated")
        self.assertEqual(second_copy.read_text(), "old")
        self.assertIn('"version": "1.2.3"', second.manifest.read_text())

    def test_invalid_manifest_prevents_all_sync_writes(self):
        self.write("skills/lucid/SKILL.md", "updated")
        old = self.write("first/skills/lucid/SKILL.md", "old")
        self.write("second/skills/lucid/SKILL.md", "old")
        first = self.target("first")
        second = self.target("second", version="bad")

        result, output = self.run_sync([first, second])
        self.assertEqual(result, 2)
        self.assertIn("numeric MAJOR.MINOR.PATCH", output)
        self.assertEqual(old.read_text(), "old")
        self.assertIn('"version": "1.2.3"', first.manifest.read_text())

    def test_invalid_manifest_is_rejected_even_without_skill_drift(self):
        self.write("skills/lucid/SKILL.md", "same")
        self.write("plugin/skills/lucid/SKILL.md", "same")
        target = self.target("plugin", version="bad")

        result, output = self.run_sync([target])
        self.assertEqual(result, 2)
        self.assertIn("numeric MAJOR.MINOR.PATCH", output)

    def test_check_rejects_bump_flag(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                sync_skills.main(["check", "--bump-version"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
