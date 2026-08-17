import unittest
from email import policy
from email.parser import BytesParser

from core.header_parser import parse_headers


class HeaderParserTests(unittest.TestCase):
    def parse(self, date_value: str):
        message = BytesParser(policy=policy.default).parsebytes(
            f"Date: {date_value}\nSubject: Test\n\nBody".encode("ascii")
        )
        return parse_headers(message)

    def test_keeps_utc_text_and_adds_jst(self):
        headers = self.parse("Sun, 17 Aug 2026 01:30:00 +0000")

        self.assertEqual("Sun, 17 Aug 2026 01:30:00 +0000", headers["date"])
        self.assertEqual("2026-08-17 10:30:00 JST", headers["date_jst"])

    def test_converts_other_explicit_timezone_to_jst(self):
        headers = self.parse("Sun, 17 Aug 2026 01:30:00 -0400")

        self.assertEqual("2026-08-17 14:30:00 JST", headers["date_jst"])

    def test_does_not_guess_timezone_when_missing(self):
        headers = self.parse("Sun, 17 Aug 2026 01:30:00")

        self.assertEqual("Sun, 17 Aug 2026 01:30:00", headers["date"])
        self.assertEqual("", headers["date_jst"])


if __name__ == "__main__":
    unittest.main()
