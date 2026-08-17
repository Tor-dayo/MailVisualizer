import tempfile
import unittest
from pathlib import Path

from core.loader import load_mail_messages


class LoadMailMessagesTests(unittest.TestCase):
    def write_temp(self, suffix: str, content: bytes) -> str:
        temp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        temp.write(content)
        temp.close()
        return temp.name

    def test_mbox_does_not_split_unescaped_from_like_body_text(self):
        content = (
            b"From alice@example.com Sat Jan  1 00:00:00 2022\n"
            b"Subject: First\n\n"
            b"Hello\n"
            b"From someone wrote this in the body\n"
            b"continued\n"
            b"From bob@example.com Sun Jan  2 00:00:00 2022\n"
            b"Subject: Second\n\nWorld\n"
        )
        path = self.write_temp(".mbox", content)

        messages = load_mail_messages(path)

        self.assertEqual(2, len(messages))
        self.assertIn(b"From someone wrote this in the body", messages[0])

    def test_mboxrd_escaped_from_is_restored_as_body_text(self):
        content = (
            b"From alice@example.com Sat Jan  1 00:00:00 2022\n"
            b"Subject: First\n\n"
            b">From quoted body line\n"
        )
        path = self.write_temp(".mbox", content)

        messages = load_mail_messages(path)

        self.assertEqual(1, len(messages))
        self.assertIn(b"From quoted body line", messages[0])

    def test_eml_is_returned_as_one_message(self):
        content = b"Subject: Single\n\nFrom body text\n"
        path = self.write_temp(".eml", content)

        self.assertEqual([content], load_mail_messages(path))


if __name__ == "__main__":
    unittest.main()
