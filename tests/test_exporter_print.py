import tempfile
import unittest
from pathlib import Path

from core.models import Mail
from exporters.exporter_print import export_print_html


class ExportPrintHtmlTests(unittest.TestCase):
    def test_generates_printable_escaped_report(self):
        mail = Mail(
            no=7,
            subject="確認 <script>",
            sender="sender@example.com",
            to="receiver@example.com",
            date="2026-08-17 10:00",
            body="一行目\nhttps://example.com/very-long-path\n<script>alert(1)</script>",
            preview="",
            message_id="<message@example.com>",
        )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "print_all.html"
            export_print_html([mail], output)
            result = output.read_text(encoding="utf-8")

        self.assertIn("@page { size: A4 portrait;", result)
        self.assertIn("window.print()", result)
        self.assertIn("page-break-after: always", result)
        self.assertIn("管理No. 7", result)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", result)
        self.assertNotIn("<script>alert(1)</script>", result)

    def test_empty_body_is_labeled(self):
        mail = Mail(1, "Empty", "", "", "", "", "", "")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "print_all.html"
            export_print_html([mail], output)
            result = output.read_text(encoding="utf-8")

        self.assertIn("本文なし", result)


if __name__ == "__main__":
    unittest.main()
