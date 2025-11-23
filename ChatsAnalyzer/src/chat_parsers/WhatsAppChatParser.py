from datetime import datetime

from src.chat_parsers.ChatParser import ChatParser
from src.chat_parsers.Message import Message


class WhatsAppChatParser(ChatParser):
    def __init__(self):
        super().__init__()

    def parse(self, data: str) -> list[Message]:
        messages = []

        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue

            if " - " not in line:
                continue

            date_part, rest = line.split(" - ", 1)

            try:
                date_str, time_str = date_part.split(", ")
                sent_at = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            except ValueError:
                continue

            if ": " not in rest:
                continue

            author, text = rest.split(": ", 1)

            text = self.clean_text(text)

            messages.append(Message(author=author, text=text, sent_at=sent_at))

        messages = self.merge_messages(messages)
        return messages
