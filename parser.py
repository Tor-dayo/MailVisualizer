import mailbox
import re
from email import policy
from email.parser import BytesParser
from email.header import decode_header
from decoder import decode_bytes, fix_text


def decode_mime_header(value):
    if not value:
        return ""

    parts = decode_header(value)
    result = ""

    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                result += part.decode(enc or "utf-8", errors="replace")
            except Exception:
                result += part.decode("utf-8", errors="replace")
        else:
            result += part

    return fix_text(result)


def get_body(message):
    body = ""

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = part.get_content_disposition()

            if disposition == "attachment":
                continue

            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body += payload.decode(charset, errors="replace")
                except Exception:
                    pass
    else:
        try:
            payload = message.get_payload(decode=True)
            if payload:
                charset = message.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")
            else:
                body = str(message.get_payload())
        except Exception:
            body = str(message.get_payload())

    return fix_text(body)


def split_raw_messages(text):
    # mbox形式: From xxx で始まるメールを分割
    pattern = r"(?m)^From .*$"
    matches = list(re.finditer(pattern, text))

    if not matches:
        return [text]

    messages = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        messages.append(text[start:end])

    return messages


def parse_mail_file(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()

    text = decode_bytes(raw)
    raw_messages = split_raw_messages(text)

    mails = []

    for idx, raw_msg in enumerate(raw_messages, start=1):
        try:
            msg = BytesParser(policy=policy.default).parsebytes(raw_msg.encode("utf-8", errors="replace"))

            subject = decode_mime_header(msg.get("Subject", ""))
            sender = decode_mime_header(msg.get("From", ""))
            to = decode_mime_header(msg.get("To", ""))
            date = decode_mime_header(msg.get("Date", ""))
            message_id = decode_mime_header(msg.get("Message-ID", ""))

            body = get_body(msg)

            if not body:
                body = fix_text(raw_msg)

            mails.append({
                "no": idx,
                "date": date,
                "from": sender,
                "to": to,
                "subject": subject,
                "body": body,
                "preview": body[:300],
                "message_id": message_id,
            })

        except Exception:
            fixed = fix_text(raw_msg)
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