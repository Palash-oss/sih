import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Prefer new official Gemini Python SDK (as of 2025)
try:  # pragma: no cover
    from google import genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # type: ignore

# Legacy SDK fallback
try:  # pragma: no cover
    import google.generativeai as genai_legacy  # type: ignore
except Exception:  # pragma: no cover
    genai_legacy = None  # type: ignore


class GeminiClient:
    """Light wrapper around Gemini API for text generation supporting multiple SDKs."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash") -> None:
        # Load .env proactively in case the app didn't yet
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv()
        except Exception:
            pass

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Allow overriding model via env
        self.model = os.getenv("GEMINI_MODEL", model)
        self._client = None
        self._mode = None  # "new" or "legacy"

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set.")
            return

        # Try new SDK first
        if genai is not None:
            try:
                self._client = genai.Client(api_key=self.api_key)
                self._mode = "new"
                logger.info(f"Initialized Gemini client using google-genai (new SDK), model={self.model}.")
                return
            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed to init new google-genai SDK: {e}")

        # Fallback to legacy SDK
        if genai_legacy is not None:
            try:
                genai_legacy.configure(api_key=self.api_key)
                self._client = genai_legacy.GenerativeModel(self.model)
                self._mode = "legacy"
                logger.info(f"Initialized Gemini client using google-generativeai (legacy SDK), model={self.model}.")
                return
            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed to init legacy google-generativeai SDK: {e}")

    def is_configured(self) -> bool:
        return self._client is not None and self._mode in ("new", "legacy")

    def generate_health_answer(self, prompt: str) -> Optional[str]:
        """Generate a concise, safety-aware health answer via Gemini.

        Returns None if client is not configured or on API errors.
        """
        if not self.is_configured():
            logger.debug("Gemini client not configured; skipping generation.")
            return None
        try:
            system_preamble = (
                "You are a multilingual healthcare information assistant. "
                "Provide evidence-based, non-diagnostic guidance, include red-flag warnings, "
                "and urge seeking professional care for emergencies. Avoid definitive diagnoses."
            )
            input_text = f"{system_preamble}\n\nUser question: {prompt}"

            if self._mode == "new":
                # google-genai new SDK uses models.generate_content; some versions don't accept generation_config
                result = self._client.models.generate_content(
                    model=self.model,
                    contents=input_text,
                )
                text = getattr(result, "text", None)
                if isinstance(text, str) and text.strip():
                    return text.strip()
                # Try candidates
                candidates = getattr(result, "candidates", None)
                if candidates:
                    for cand in candidates:
                        txt = getattr(cand, "text", None)
                        if txt:
                            return txt.strip()
                logger.debug("New SDK returned no text.")
                return None

            # Legacy
            if self._mode == "legacy":
                result = self._client.generate_content(
                    input_text,
                    generation_config={
                        "temperature": 0.4,
                        "max_output_tokens": 512,
                    },
                )
                # Legacy SDK often has .text
                text = getattr(result, "text", None)
                if isinstance(text, str) and text.strip():
                    return text.strip()
                # Some versions use .candidates[0].content.parts[0].text
                try:
                    for cand in getattr(result, "candidates", []) or []:
                        parts = getattr(getattr(cand, "content", None), "parts", []) or []
                        for part in parts:
                            txt = getattr(part, "text", None)
                            if txt:
                                return txt.strip()
                except Exception:
                    pass
                logger.debug("Legacy SDK returned no text.")
                return None

            return None
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None


