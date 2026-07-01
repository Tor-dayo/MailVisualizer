from email import policy
from email.parser import BytesParser

from core.loader import load_raw_file, split_mbox_messages
from core.models import Mail
from core.header_parser import parse_headers
from core.body_parser import extract_body


def parse_mail_file(file_path):
    raw = load_raw_file(file_path)
    raw_messages = split_mbox_messages(raw)

    mails = []

    for no, raw_message in enumerate(raw_messages, start=1):
        try:
            email_message = BytesParser(policy=policy.default).parsebytes(raw_message)

            headers = parse_headers(email_message)
            body = extract_body(email_message)

            mails.append(
                Mail(
                    no=no,
                    subject=headers.get("subject", "") or f"件名なし {no}",
                    sender=headers.get("from", ""),
                    to=headers.get("to", ""),
                    date=headers.get("date", ""),
                    body=body,
                    preview=body[:300],
                    message_id=headers.get("message_id", ""),
                )
            )

        except Exception as e:
            error_text = f"解析失敗: {e}"

            mails.append(
                Mail(
                    no=no,
                    subject=f"解析失敗メール {no}",
                    sender="",
                    to="",
                    date="",
                    body=error_text,
                    preview=error_text,
                    message_id="",
                )
            )

    return mails