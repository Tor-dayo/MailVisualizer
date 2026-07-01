from bs4 import BeautifulSoup

from core.decoder import decode_payload, clean_text


def html_to_text(html: str) -> str:
    if not html:
        return ""

    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text("\n")
    except Exception:
        return html


def extract_body(message) -> str:
    plain_parts = []
    html_parts = []

    if message.is_multipart():
        for part in message.walk():
            disposition = part.get_content_disposition()
            content_type = part.get_content_type()

            if disposition == "attachment":
                continue

            if content_type not in ("text/plain", "text/html"):
                continue

            charset = part.get_content_charset()
            payload = part.get_payload(decode=True)

            if payload is None:
                payload = part.get_payload()

            text = decode_payload(payload, charset)

            if not text:
                continue

            if content_type == "text/plain":
                plain_parts.append(text)

            elif content_type == "text/html":
                html_parts.append(html_to_text(text))

    else:
        charset = message.get_content_charset()
        content_type = message.get_content_type()
        payload = message.get_payload(decode=True)

        if payload is None:
            payload = message.get_payload()

        text = decode_payload(payload, charset)

        if content_type == "text/html":
            return clean_text(html_to_text(text))

        return clean_text(text)

    if plain_parts:
        return clean_text("\n\n".join(plain_parts))

    if html_parts:
        return clean_text("\n\n".join(html_parts))

    return ""