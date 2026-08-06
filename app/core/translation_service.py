"""多引擎中文翻译服务。"""
from __future__ import annotations

from dataclasses import dataclass
import json
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request


ENGINE_DEFAULT_URLS = {
    "Google": "https://translate.googleapis.com/translate_a/single",
    "MyMemory（免费）": "https://api.mymemory.translated.net/get",
    "LibreTranslate": "https://libretranslate.com/translate",
    "AI 大模型": "http://127.0.0.1:11434/v1/chat/completions",
}

TARGET_LANGUAGE_CODES = {
    "英语": "en",
    "日语": "ja",
    "韩语": "ko",
    "法语": "fr",
    "德语": "de",
    "西班牙语": "es",
    "俄语": "ru",
    "意大利语": "it",
}


@dataclass
class TranslationSettings:
    engine: str = "Google"
    api_url: str = ENGINE_DEFAULT_URLS["Google"]
    api_key: str = ""
    model: str = "qwen2.5:7b"
    prompt: str = (
        "你是一名专业翻译。请将以下{from}翻译成{to}。\n"
        "只输出译文，不要解释，不要输出原文。"
    )


class TranslationService:
    """根据设置调用免费翻译接口或 OpenAI 兼容 AI 接口。"""

    def __init__(self, settings: TranslationSettings) -> None:
        self.settings = settings

    def translate(self, chinese_text: str, target_language: str) -> str:
        text = chinese_text.strip()
        if not text:
            return ""
        target_code = TARGET_LANGUAGE_CODES.get(target_language, "en")
        engine = self.settings.engine
        if engine == "Google":
            return self._google(text, target_code)
        if engine == "MyMemory（免费）":
            return self._mymemory(text, target_code)
        if engine == "LibreTranslate":
            return self._libretranslate(text, target_code)
        if engine == "AI 大模型":
            return self._ai_model(text, target_language)
        raise RuntimeError(f"不支持的翻译引擎：{engine}")

    def _google(self, text: str, target_code: str) -> str:
        query = urllib_parse.urlencode(
            {
                "client": "gtx",
                "sl": "zh-CN",
                "tl": target_code,
                "dt": "t",
                "q": text,
            }
        )
        result = self._get_json(f"{self.settings.api_url}?{query}")
        try:
            parts = [item[0] for item in result[0] if item and item[0]]
        except (IndexError, KeyError, TypeError) as exc:
            raise RuntimeError("Google 翻译返回格式异常") from exc
        return "".join(parts).strip()

    def _mymemory(self, text: str, target_code: str) -> str:
        query = urllib_parse.urlencode(
            {
                "q": text,
                "langpair": f"zh-CN|{target_code}",
            }
        )
        result = self._get_json(f"{self.settings.api_url}?{query}")
        try:
            return str(result["responseData"]["translatedText"]).strip()
        except (KeyError, TypeError) as exc:
            raise RuntimeError("MyMemory 翻译返回格式异常") from exc

    def _libretranslate(self, text: str, target_code: str) -> str:
        body = {"q": text, "source": "zh", "target": target_code, "format": "text"}
        if self.settings.api_key.strip():
            body["api_key"] = self.settings.api_key.strip()
        result = self._post_json(self.settings.api_url, body)
        try:
            return str(result["translatedText"]).strip()
        except (KeyError, TypeError) as exc:
            raise RuntimeError("LibreTranslate 翻译返回格式异常") from exc

    def _ai_model(self, text: str, target_language: str) -> str:
        prompt = self.settings.prompt or TranslationSettings().prompt
        prompt = prompt.replace("{from}", "中文").replace("{to}", target_language)
        result = self._post_json(
            self.settings.api_url,
            {
                "model": self.settings.model.strip(),
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
            },
        )
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("AI 接口返回格式不是 OpenAI Chat Completions 格式") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("接口没有返回翻译内容")
        return content.strip()

    def _get_json(self, url: str):
        request = urllib_request.Request(url, headers={"User-Agent": "ChineseTranslator/1.0"})
        try:
            with urllib_request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            raise RuntimeError(f"翻译接口返回 HTTP {exc.code}") from exc
        except urllib_error.URLError as exc:
            raise RuntimeError(f"无法连接翻译接口：{exc.reason}") from exc

    def _post_json(self, url: str, body: dict):
        headers = {"Content-Type": "application/json", "User-Agent": "ChineseTranslator/1.0"}
        if self.settings.api_key.strip():
            headers["Authorization"] = f"Bearer {self.settings.api_key.strip()}"
        request = urllib_request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib_request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"翻译接口返回 HTTP {exc.code}: {detail}") from exc
        except urllib_error.URLError as exc:
            raise RuntimeError(f"无法连接翻译接口：{exc.reason}") from exc
