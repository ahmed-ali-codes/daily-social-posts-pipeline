import urllib.request
import urllib.parse
import json
import ssl
import time
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """Enterprise LLM Client with automatic fallback and retries."""
    
    OPENROUTER_MODELS = [
        "google/gemma-2-27b-it",
        "nvidia/nemotron-mini-4b-instruct",
        "qwen/qwen-2-7b-instruct"
    ]

    def __init__(self, openrouter_key: str, gemini_key: str):
        self.openrouter_key = openrouter_key
        self.gemini_key = gemini_key
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def call_openrouter(self, system_prompt: str, user_prompt: str, max_tokens: int = 3000) -> str:
        if not self.openrouter_key:
            return None
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json"
        }
        for model in self.OPENROUTER_MODELS:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": max_tokens
            }
            for attempt in range(3):
                try:
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers=headers,
                        method="POST"
                    )
                    with urllib.request.urlopen(req, context=self.ctx, timeout=45) as res:
                        resp = json.loads(res.read().decode("utf-8"))
                        if resp and "choices" in resp and resp["choices"]:
                            text = resp["choices"][0]["message"]["content"].strip()
                            if text and len(text) > 50:
                                logger.info(f"  ✓ Generated via OpenRouter ({model})")
                                return text
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        logger.warning(f"  Rate limited on {model}, retrying in {8*(attempt+1)}s...")
                        time.sleep(8 * (attempt + 1))
                    else:
                        logger.warning(f"  HTTP {e.code} on {model}, trying next model...")
                        break
                except Exception as e:
                    logger.error(f"  Error on {model}: {e}, trying next...")
                    break
            time.sleep(2)
        return None

    def call_gemini_direct(self, system_prompt: str, user_prompt: str, max_tokens: int = 3000) -> str:
        if not self.gemini_key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8}
        }
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, context=self.ctx, timeout=45) as res:
                    resp = json.loads(res.read().decode("utf-8"))
                    text = resp["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text and len(text) > 50:
                        logger.info(f"  ✓ Generated via Gemini API (direct)")
                        return text
            except Exception as e:
                logger.error(f"  Gemini attempt {attempt+1} failed: {e}")
                time.sleep(5)
        return None

    def call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 3000, fallback_text: str = None) -> str:
        """Try OpenRouter models, then Gemini direct, then return fallback."""
        result = self.call_openrouter(system_prompt, user_prompt, max_tokens)
        if result:
            return result
        logger.info("  OpenRouter exhausted, trying Gemini API...")
        result = self.call_gemini_direct(system_prompt, user_prompt, max_tokens)
        if result:
            return result
        if fallback_text:
            logger.warning("  ⚠ All LLMs failed. Using fallback stub.")
            return fallback_text
        logger.error("  ✗ All LLM options failed for this post.")
        return None
