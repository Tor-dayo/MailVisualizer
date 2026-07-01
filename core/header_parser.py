from email.header import decode_header


def decode_text(value):
    """
    MIMEヘッダを人間が読める文字列へ変換する
    """

    if not value:
        return ""

    result = ""

    for part, encoding in decode_header(value):

        if isinstance(part, bytes):

            encodings = []

            if encoding:
                encodings.append(encoding)

            encodings += [
                "utf-8",
                "iso-2022-jp",
                "cp932",
                "shift_jis",
                "euc_jp",
            ]

            decoded = None

            for enc in encodings:

                try:
                    decoded = part.decode(enc)
                    break
                except Exception:
                    pass

            if decoded is None:
                decoded = part.decode("utf-8", errors="replace")

            result += decoded

        else:
            result += str(part)

    return result.strip()


def parse_headers(message):
    """
    EmailMessageからヘッダだけ取得
    """

    return {

        "subject": decode_text(message.get("Subject", "")),

        "from": decode_text(message.get("From", "")),

        "to": decode_text(message.get("To", "")),

        "date": decode_text(message.get("Date", "")),

        "message_id": decode_text(message.get("Message-ID", "")),
    }