from email import policy
from email.parser import BytesParser
import re

from decoder import decode_mime_header, decode_payload, clean_text


def split_raw_messages_bytes(raw: bytes):
    # mbox形式の「From 〜」で分割
    pattern = re.compile(rb"(?m)^From .*$")
    matches = list(pattern.finditer(raw))

    if not matches:
        return [raw]

    messages = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        messages.append(raw[start:end])

    return messages


def get_best_body(message):
    plain_body = ""
    html_body = ""

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue

            content_type = part.get_content_type()
            charset = part.get_content_charset()

            payload = part.get_payload(decode=True)
            if payload is None:
                payload = part.get_payload()

            decoded = decode_payload(payload, charset)

            if content_type == "text/plain":
                plain_body += decoded + "\n\n"
            elif content_type == "text/html":
                html_body += decoded + "\n\n"
    else:
        charset = message.get_content_charset()
        payload = message.get_payload(decode=True)
        if payload is None:
            payload = message.get_payload()
        plain_body = decode_payload(payload, charset)

    if plain_body.strip():
        return clean_text(plain_body)

    if html_body.strip():
        return clean_text(html_body)

    return ""


def parse_one_message(raw_message: bytes, no: int):
    msg = BytesParser(policy=policy.default).parsebytes(raw_message)

    subject = decode_mime_header(msg.get("Subject", ""))
    sender = decode_mime_header(msg.get("From", ""))
    to = decode_mime_header(msg.get("To", ""))
    date = decode_mime_header(msg.get("Date", ""))
    message_id = decode_mime_header(msg.get("Message-ID", ""))

    body = get_best_body(msg)

    if not body:
        body = decode_payload(raw_message)

    return {
        "no": no,
        "date": date,
        "from": sender,
        "to": to,
        "subject": subject or f"件名なし {no}",
        "body": body,
        "preview": body[:300],
        "message_id": message_id,
    }


def parse_mail_file(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()

    raw_messages = split_raw_messages_bytes(raw)

    mails = []

    for idx, raw_msg in enumerate(raw_messages, start=1):
        try:
            mails.append(parse_one_message(raw_msg, idx))
        except Exception:
            fixed = clean_text(decode_payload(raw_msg))
            mails.append({
                "no": idx,
                "date": "",
                "from": "",
                "to": "",
                "subject": f"解析失敗メール {idx}",
                "body": fixed,
                "preview": fixed[:300],
                "message_id": "",
            })

    return mails