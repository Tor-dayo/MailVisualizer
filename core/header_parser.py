from email.header import decode_header
from datetime import timezone, timedelta
from email.utils import parsedate_to_datetime


JST = timezone(timedelta(hours=9))


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

    raw_date = next(
        (value for name, value in message.raw_items() if name.lower() == "date"),
        "",
    )
    original_date = decode_text(raw_date)

    try:
        parsed_date = parsedate_to_datetime(original_date)
        date_jst = (
            parsed_date.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S JST")
            if parsed_date.tzinfo is not None
            else ""
        )
    except (TypeError, ValueError, OverflowError):
        date_jst = ""

    return {

        "subject": decode_text(message.get("Subject", "")),

        "from": decode_text(message.get("From", "")),

        "to": decode_text(message.get("To", "")),

        "date": original_date,

        "date_jst": date_jst,

        "message_id": decode_text(message.get("Message-ID", "")),
    }
