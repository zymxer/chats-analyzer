import json

from fastapi import APIRouter, UploadFile, File, Form

from src.chat_parsers.TelegramChatParser import TelegramChatParser
from src.chat_parsers.WhatsAppChatParser import WhatsAppChatParser

router = APIRouter()
telegramParser = TelegramChatParser()
whatsAppParser = WhatsAppChatParser()


@router.post("/parse/tg",
             summary="Parse Telegram chat from .json file",
             response_description=".jsonl string for model tuning"
             )
async def parse_telegram_chat(
        output_author: str = Form(...),
        chat: UploadFile = File(...)
):
    bytes = await chat.read()
    chat_text = json.loads(bytes.decode("utf-8"))
    messages = telegramParser.parse(chat_text)
    return telegramParser.to_jsonl(messages, output_author)


@router.post("/parse/wa",
             summary="Parse WhatsApp chat from .txt file",
             response_description=".jsonl string for model tuning"
             )
async def parse_whatsapp_chat(
        output_author: str = Form(...),
        chat: UploadFile = File(...)
):
    bytes = await chat.read()
    chat_text = bytes.decode("utf-8")
    messages = whatsAppParser.parse(chat_text)
    return whatsAppParser.to_jsonl(messages, output_author)
