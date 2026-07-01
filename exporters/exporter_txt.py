import os
import re


def safe_filename(text):
    text = text or "no_subject"
    text = re.sub(r'[\\/:*?"<>|]', "_", text)
    text = text.strip()
    return text[:50]


def export_txt_files(mails, output_folder):
    mails_folder = os.path.join(output_folder, "mails")
    os.makedirs(mails_folder, exist_ok=True)

    for mail in mails:
        no = str(mail["no"]).zfill(4)
        subject = safe_filename(mail["subject"])
        filename = f"{no}_{subject}.txt"
        path = os.path.join(mails_folder, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"件名: {mail['subject']}\n")
            f.write(f"日時: {mail['date']}\n")
            f.write(f"差出人: {mail['from']}\n")
            f.write(f"宛先: {mail['to']}\n")
            f.write(f"Message-ID: {mail['message_id']}\n")
            f.write("\n" + "=" * 60 + "\n\n")
            f.write(mail["body"])