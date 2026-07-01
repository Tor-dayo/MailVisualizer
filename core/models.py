from dataclasses import dataclass


@dataclass
class Mail:

    no: int

    subject: str

    sender: str

    to: str

    date: str

    body: str

    preview: str

    message_id: str