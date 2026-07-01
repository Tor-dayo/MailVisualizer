import os

from core.parser import parse_mail_file
from exporters.exporter_excel import export_excel
from exporters.exporter_html import export_html
from exporters.exporter_txt import export_txt_files


class MailService:
    def convert(
        self,
        input_file,
        output_folder,
        excel=True,
        html=True,
        txt=True,
    ):
        os.makedirs(output_folder, exist_ok=True)

        mails = parse_mail_file(input_file)

        if excel:
            export_excel(
                mails,
                os.path.join(output_folder, "mail_index.xlsx"),
            )

        if html:
            export_html(
                mails,
                os.path.join(output_folder, "index.html"),
            )

        if txt:
            export_txt_files(
                mails,
                output_folder,
            )

        return mails