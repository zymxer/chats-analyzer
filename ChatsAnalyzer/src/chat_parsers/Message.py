from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    author: str
    sent_at: datetime
    text: str
