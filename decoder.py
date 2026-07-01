import base64
import quopri
import html
import re


def fix_text(text: str) -> str:
    if not text:
        return ""

    # \u3053\u306e... 形式を日本語に戻す
    if "\\u" in text:
        try:
            text = text.encode("utf-8").decode("unicode_escape")
        except Exception:
            pass

    # HTMLエスケープ解除
    text = html.unescape(text)

    # 改行・空白整理
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def decode_bytes(data: bytes) -> str:
    encodings = [
        "utf-8",
        "utf-8-sig",
        "iso-2022-jp",
        "cp932",
        "shift_jis",
        "euc_jp",
        "latin1",
    ]

    for enc in encodings:
        try:
            return data.decode(enc)
        except Exception:
            pass

    return data.decode("utf-8", errors="replace")