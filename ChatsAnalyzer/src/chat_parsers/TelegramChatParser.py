from datetime import datetime

from src.chat_parsers.ChatParser import ChatParser
from src.chat_parsers.Message import Message


class TelegramChatParser(ChatParser):
    def __init__(self):
        super().__init__()

    def parse(self, data) -> list[Message]:
        messages = []
        for msg in data.get("messages", []):
            text_entities = msg.get("text_entities", [])
            if not text_entities:
                continue
            parts = []
            for part in text_entities:
                text = part.get("text")
                text = self.clean_text(text)
                parts.append(text)

            author = msg.get("from", "")
            forwarded_from = msg.get("forwarded_from", "")
            if forwarded_from:
                author = forwarded_from

            sent_at = datetime.fromisoformat(msg.get("date"))

            messages.append(Message(author=author, text="".join(parts), sent_at=sent_at))

        messages = self.merge_messages(messages)

        return messages
