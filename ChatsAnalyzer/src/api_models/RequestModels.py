from pydantic import BaseModel

class TelegramChatRequest(BaseModel):
    output_author: str
    chat: UploadFile = File(...)

class WhatsAppChatRequest(BaseModel):
    chat: str

class FactsRequest(BaseModel):
    jsonl: str

