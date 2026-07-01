import re


def load_raw_file(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def split_mbox_messages(raw: bytes) -> list[bytes]:
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