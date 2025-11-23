from langdetect import detect, LangDetectException
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class Translator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def translate(self, text: str, source_lang: str = None, target_lang: str = None) -> str:
        if source_lang and hasattr(self.tokenizer, "src_lang"):
            self.tokenizer.src_lang = source_lang

        encoded = self.tokenizer(text, return_tensors="pt", padding=True)

        kwargs = {}
        if target_lang and hasattr(self.tokenizer, "get_lang_id"):
            kwargs["forced_bos_token_id"] = self.tokenizer.get_lang_id(target_lang)

        output = self.model.generate(**encoded, **kwargs)
        decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded

    #Todo divide text into batches of different languages
    def translate_batch(self, texts: list[str], source_lang: str = None, target_lang: str = None) -> list[str]:
        if source_lang and hasattr(self.tokenizer, "src_lang"):
            self.tokenizer.src_lang = source_lang

        encoded = self.tokenizer(texts, return_tensors="pt", padding=True)

        kwargs = {}
        if target_lang and hasattr(self.tokenizer, "get_lang_id"):
            kwargs["forced_bos_token_id"] = self.tokenizer.get_lang_id(target_lang)

        output = self.model.generate(**encoded, **kwargs)
        return self.tokenizer.batch_decode(output, skip_special_tokens=True)

    def detect_lang(self, text: str) -> str:
        try:
            return detect(text)
        except LangDetectException:
            return "en"