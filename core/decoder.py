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
    "iso-2022-jp",
    "utf-8",
    "utf-8-sig",
    "cp932",
    "shift_jis",
    "euc_jp",
    "latin1",
]


def normalize_charset(charset):
    if not charset:
        return None

    charset = charset.lower().replace("_", "-").strip()

    alias = {
        "iso2022jp": "iso-2022-jp",
        "iso-2022-jp": "iso-2022-jp",
        "shift-jis": "shift_jis",
        "windows-31j": "cp932",
        "sjis": "shift_jis",
    }

    return alias.get(charset, charset)


def repair_iso2022jp_text(text: str) -> str:
    if not text:
        return ""

    if "$B" not in text and "(B" not in text:
        return text

    try:
        fixed = text.replace("$B", "\x1b$B").replace("(B", "\x1b(B")
        return fixed.encode("latin1", errors="ignore").decode("iso-2022-jp", errors="replace")
    except Exception:
        return text


def badness(text: str) -> int:
    return (
        text.count("�") * 10
        + text.count("\x00") * 20
        + text.count("$B") * 30
    )


def decode_bytes(data: bytes, charset: str | None = None) -> str:
    if data is None:
        return ""

    charset = normalize_charset(charset)

    if charset:
        try:
            return data.decode(charset)
        except Exception:
            pass

    candidates = []

    for enc in ENCODINGS:
        try:
            candidates.append(data.decode(enc, errors="replace"))
        except Exception:
            pass

    if chardet:
        try:
            guessed = normalize_charset(chardet.detect(data).get("encoding"))
            if guessed:
                candidates.append(data.decode(guessed, errors="replace"))
        except Exception:
            pass

    return min(candidates, key=badness) if candidates else data.decode("utf-8", errors="replace")


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


def html_to_text(text: str) -> str:
    if not text:
        return ""

    lower = text.lower()

    if "<html" in lower or "<body" in lower or "<!doctype" in lower:
        try:
            soup = BeautifulSoup(text, "html.parser")
            return soup.get_text("\n")
        except Exception:
            text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
            text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", "\n", text)
            return text

    return text


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = html.unescape(text)
    text = repair_iso2022jp_text(text)
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

    candidates = []

    candidates.append(decode_bytes(payload, charset))

    try:
        qp = quopri.decodestring(payload)
        candidates.append(decode_bytes(qp, charset))
    except Exception:
        pass

    try:
        compact = re.sub(rb"\s+", b"", payload)
        if len(compact) > 20:
            b64 = base64.b64decode(compact, validate=True)
            candidates.append(decode_bytes(b64, charset))
    except Exception:
        pass

    best = min(candidates, key=badness)

    return clean_text(best)