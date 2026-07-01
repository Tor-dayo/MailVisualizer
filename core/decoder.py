import re
import html
import base64
import quopri
from email.header import decode_header
from bs4 import BeautifulSoup

try:
    import chardet
except Exception:
    chardet = None


ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "iso-2022-jp",
    "cp932",
    "shift_jis",
    "euc_jp",
    "latin1",
]


def decode_bytes(data: bytes, charset: str | None = None) -> str:
    if data is None:
        return ""

    if charset:
        try:
            return data.decode(charset, errors="replace")
        except Exception:
            pass

    for enc in ENCODINGS:
        try:
            return data.decode(enc)
        except Exception:
            pass

    if chardet:
        try:
            guessed = chardet.detect(data)
            enc = guessed.get("encoding")
            if enc:
                return data.decode(enc, errors="replace")
        except Exception:
            pass

    return data.decode("utf-8", errors="replace")


def decode_mime_header(value) -> str:
    if not value:
        return ""

    result = ""

    for part, enc in decode_header(value):
        if isinstance(part, bytes):
            result += decode_bytes(part, enc)
        else:
            result += str(part)

    return clean_text(result)


def maybe_unicode_escape(text: str) -> str:
    if not text:
        return ""

    # \u3053\u306e 形式を戻す
    if "\\u" in text:
        try:
            return text.encode("utf-8").decode("unicode_escape")
        except Exception:
            return text

    return text


def html_to_text(text: str) -> str:
    if not text:
        return ""

    if "<html" in text.lower() or "<body" in text.lower() or "<!doctype" in text.lower():
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text("\n")

    return text


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = maybe_unicode_escape(text)
    text = html.unescape(text)
    text = html_to_text(text)

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def decode_payload(payload: bytes | str | None, charset: str | None = None) -> str:
    if payload is None:
        return ""

    if isinstance(payload, str):
        return clean_text(payload)

    # まず普通にデコード
    text = decode_bytes(payload, charset)

    # quoted-printableっぽい場合
    if "=" in text and re.search(r"=[0-9A-Fa-f]{2}", text):
        try:
            qp = quopri.decodestring(payload)
            text = decode_bytes(qp, charset)
        except Exception:
            pass

    # base64っぽい場合
    compact = re.sub(rb"\s+", b"", payload)
    if len(compact) > 20:
        try:
            b64 = base64.b64decode(compact, validate=True)
            decoded = decode_bytes(b64, charset)
            if len(decoded) > len(text) / 2:
                text = decoded
        except Exception:
            pass

    return clean_text(text)