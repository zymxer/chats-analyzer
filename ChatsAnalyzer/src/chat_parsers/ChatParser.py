import json
import re
from abc import ABC, abstractmethod
from datetime import datetime

import emoji

from src.chat_parsers.Message import Message
from src.config import MESSAGES_MERGE_TIME_LIMIT


class ChatParser(ABC):
    @abstractmethod
    def parse(self, data) -> list[Message]:
        pass

    def merge_messages(self, messages: list[Message], limit_sec: int = MESSAGES_MERGE_TIME_LIMIT) -> list[Message]:
        merged_messages = []
        current_message = messages[0]
        for i, message in enumerate(messages):
            if current_message is message:
                if i == len(messages) - 1:
                    merged_messages.append(current_message)
                continue

            if current_message.author != message.author:
                merged_messages.append(current_message)
                current_message = message
                if i == len(messages) - 1:
                    merged_messages.append(current_message)
                continue

            if self._within_time_limit(current_message.sent_at, message.sent_at, limit_sec):
                current_message.text = current_message.text + " " + message.text
                current_message.sent_at = message.sent_at
            else:
                merged_messages.append(current_message)
                current_message = message
            if i == len(messages) - 1:
                merged_messages.append(current_message)
        return merged_messages

    def _within_time_limit(self, date1: datetime, date2: datetime, limit_sec: int) -> bool:
        return True
        #diff = date2 - date1
        #return diff.total_seconds() < limit_sec

    def clean_text(self, text: str) -> str:
        text = re.sub(r'[\t\n\r\f\v]+', ' ', text)
        text = re.sub(r' +', ' ', text).strip()
        text = emoji.demojize(text)
        return text

    def to_jsonl(self, messages: list[Message], output_author: str) -> str:
        jsonl_lines = []

        for i, msg in enumerate(messages):
            if msg.author == output_author and i > 0:
                prev_msg = messages[i - 1]
                entry = {
                    "input": f"{prev_msg.author}: {prev_msg.text}",
                    "output": f"{msg.author}: {msg.text}"
                }
                jsonl_lines.append(json.dumps(entry, ensure_ascii=False))

        return "\n".join(jsonl_lines)
