"""Package integrity checks: no model, host or human experiment is run here."""
from __future__ import annotations
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class MaterialChecks(unittest.TestCase):
    def test_original_files_unchanged(self):
        data = json.loads((ROOT / "records/source_files.json").read_text(encoding="utf-8"))
        for item in data["files"]:
            p = ROOT / item["path"]
            self.assertTrue(p.is_file(), str(p))
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), item["source_sha256"], str(p))

    def test_s1_and_s2_have_all_source_sections(self):
        s1 = (ROOT / "docs/S1_signal_verification.md").read_text(encoding="utf-8")
        s2 = (ROOT / "docs/S2_listening_protocol.md").read_text(encoding="utf-8")
        for n in (1, 2):
            self.assertIn(f'S1.{n}', s1)
        for n in range(1, 8):
            self.assertIn(f'S2.{n}', s2)
        self.assertIn('id="s2-2"', s2)
        self.assertIn('id="s2-6"', s2)
        self.assertIn('每项保护损失', s2)
        self.assertIn('尚未开展', s2)

    def test_reference_and_reproduction_are_separate(self):
        self.assertTrue((ROOT / "records/reference/component_results.json").is_file())
        self.assertTrue((ROOT / "records/reproductions/package_check/component_results.json").is_file())
        a = ROOT / "records/reference/analytical_candidates.json"
        b = ROOT / "records/reproductions/package_check/analytical_candidates.json"
        self.assertEqual(json.loads(a.read_text()), json.loads(b.read_text()))

    def test_local_markdown_links_resolve(self):
        for p in ROOT.rglob("*.md"):
            text = p.read_text(encoding="utf-8")
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#') or target.startswith('mailto:'):
                    continue
                path = target.split('#', 1)[0]
                self.assertTrue((p.parent / path).exists(), f'{p.relative_to(ROOT)} -> {target}')

    def test_private_documents_not_in_public_tree(self):
        for p in ROOT.rglob('*'):
            self.assertNotIn(p.suffix.lower(), {'.docx', '.doc', '.pdf', '.zip', '.ttf', '.otf'})
            self.assertNotIn('author_only', p.relative_to(ROOT).parts)
        self.assertFalse((ROOT / '.env').exists())

if __name__ == '__main__':
    unittest.main()
