import json
import re
import tempfile
import unittest
from pathlib import Path

from core.models import Mail
from exporters.exporter_html import export_html


class ExportHtmlTests(unittest.TestCase):
    def test_contains_multi_filter_and_sort_controls(self):
        mail = Mail(1, "件名", "a@example.jp", "b@example.jp", "2026-08-17", "本文", "", "<id>")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            export_html([mail], output)
            result = output.read_text(encoding="utf-8")

        self.assertIn("絞り込み条件（AND）", result)
        self.assertIn("並べ替え条件", result)
        self.assertIn('id="add-filter"', result)
        self.assertIn('id="add-sort"', result)
        self.assertIn("filterConditions.every", result)
        self.assertIn("for(const c of sortConditions)", result)

    def test_embedded_data_cannot_close_script_element(self):
        subject = "</script><script>alert(1)</script>"
        mail = Mail(1, subject, "", "", "", "<b>body</b>", "", "")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            export_html([mail], output)
            result = output.read_text(encoding="utf-8")

        match = re.search(r'<script id="mail-data" type="application/json">(.*?)</script>', result, re.DOTALL)
        self.assertIsNotNone(match)
        payload = match.group(1)
        self.assertNotIn("</script>", payload.lower())
        self.assertEqual(subject, json.loads(payload)[0]["subject"])


if __name__ == "__main__":
    unittest.main()
