"""Tests for generating the awesome-copilot plugin directory from lucid/."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts import sync_awesome_copilot_plugin


class CopilotManifestTests(unittest.TestCase):
    def manifest(self, keywords):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "plugin.json"
        path.write_text(json.dumps({"name": "lucid", "version": "1.0.0", "keywords": keywords}))
        return path

    def test_keeps_first_ten_keywords_in_order(self):
        keywords = [f"tag-{i}" for i in range(15)]
        result = json.loads(sync_awesome_copilot_plugin.awesome_copilot_manifest(self.manifest(keywords)))
        self.assertEqual(result["keywords"], keywords[:10])
        self.assertEqual(result["version"], "1.0.0")

    def test_short_keyword_list_is_unchanged(self):
        result = json.loads(sync_awesome_copilot_plugin.awesome_copilot_manifest(self.manifest(["a", "b"])))
        self.assertEqual(result["keywords"], ["a", "b"])

    def test_invalid_kept_keyword_is_an_error(self):
        with self.assertRaises(sync_awesome_copilot_plugin.SyncError):
            sync_awesome_copilot_plugin.awesome_copilot_manifest(self.manifest(["Not Valid"]))

    def test_invalid_keyword_beyond_limit_is_ignored(self):
        keywords = [f"tag-{i}" for i in range(10)] + ["Not Valid"]
        result = json.loads(sync_awesome_copilot_plugin.awesome_copilot_manifest(self.manifest(keywords)))
        self.assertEqual(len(result["keywords"]), 10)


if __name__ == "__main__":
    unittest.main()
