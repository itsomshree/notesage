import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

HF_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
CHAT_COMPLETIONS_URL = "https://router.huggingface.co/v1/chat/completions"

MODEL_FALLBACKS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
]

MAX_RETRIES_PER_MODEL = 2
BACKOFF_SECONDS = 2
REQUEST_TIMEOUT = 30


class HFInferenceError(Exception):
    """Raised when every model/provider fallback has been exhausted."""


def _call_once(model: str, messages: list[dict], **kwargs) -> str:
    if not HF_TOKEN:
        raise RuntimeError("HUGGINGFACEHUB_API_TOKEN is not set (check your .env)")

    response = requests.post(
        CHAT_COMPLETIONS_URL,
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.3),
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def chat_completion(messages: list[dict], **kwargs) -> str:
    last_exc: Exception | None = None

    for model in MODEL_FALLBACKS:
        for attempt in range(1, MAX_RETRIES_PER_MODEL + 1):
            try:
                return _call_once(model, messages, **kwargs)
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_exc = exc
                logger.warning(
                    "HF call timed out (%s/%s) model=%s",
                    attempt,
                    MAX_RETRIES_PER_MODEL,
                    model,
                )
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                last_exc = exc
                if status and status < 500 and status != 429:
                    # Client error (bad request, auth, etc.) — retrying won't help.
                    body = exc.response.text[:500] if exc.response is not None else ""
                    logger.error(
                        "HF call failed with non-retryable status %s model=%s body=%s",
                        status,
                        model,
                        body,
                    )
                    break
                logger.warning(
                    "HF call failed (%s/%s) status=%s model=%s",
                    attempt,
                    MAX_RETRIES_PER_MODEL,
                    status,
                    model,
                )

            if attempt < MAX_RETRIES_PER_MODEL:
                time.sleep(BACKOFF_SECONDS * attempt)

        logger.error("Exhausted retries for model=%s, trying next fallback", model)

    raise HFInferenceError(
        f"All HF model fallbacks failed. Last error: {last_exc}"
    ) from last_exc
