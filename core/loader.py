import re
from pathlib import Path


HEADER_LINE = re.compile(rb"^[!-9;-~]+:")
COMMON_HEADERS = {
    b"date",
    b"from",
    b"message-id",
    b"mime-version",
    b"received",
    b"return-path",
    b"subject",
    b"to",
}


def load_raw_file(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def _looks_like_mbox(file_path: str, raw: bytes) -> bool:
    """拡張子または先頭のUnix From行からmboxかどうかを判定する。"""
    return Path(file_path).suffix.lower() == ".mbox" or raw.startswith(b"From ")


def _is_message_separator(lines: list[bytes], index: int) -> bool:
    """From行の直後がRFC形式のヘッダブロックなら境界とみなす。"""
    if not lines[index].startswith(b"From "):
        return False

    found_common_header = False

    for line in lines[index + 1 : index + 101]:
        stripped = line.rstrip(b"\r\n")

        if not stripped:
            return found_common_header

        if stripped.startswith((b" ", b"\t")):
            continue

        if not HEADER_LINE.match(stripped):
            return False

        name = stripped.split(b":", 1)[0].lower()
        found_common_header = found_common_header or name in COMMON_HEADERS

    return False


def _split_mbox_messages(raw: bytes) -> list[bytes]:
    lines = raw.splitlines(keepends=True)
    separators = [
        index for index in range(len(lines)) if _is_message_separator(lines, index)
    ]

    if not separators:
        return [raw]

    messages = []

    for position, separator in enumerate(separators):
        start = separator + 1
        end = separators[position + 1] if position + 1 < len(separators) else len(lines)
        message = b"".join(lines[start:end])
        # mboxrdで本文行頭のFromを保護するために付けられた引用符を戻す。
        messages.append(re.sub(rb"(?m)^>From ", b"From ", message))

    return messages


def load_mail_messages(file_path: str) -> list[bytes]:
    """mboxは標準ライブラリで読み、eml等は単一メールとして返す。"""
    raw = load_raw_file(file_path)

    if not _looks_like_mbox(file_path, raw):
        return [raw]

    return _split_mbox_messages(raw)
