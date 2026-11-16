"""
Thin wrapper around Claude (Anthropic Messages API).

The rest of the system never imports `anthropic` directly. It asks this module
for an LLM and gets either a working ClaudeLLM or None. None means "run the
offline path" (rule-based parser + template writer), so the project works and
can be graded without an API key.

Configuration (environment variables or a local .env file, never committed):
  ANTHROPIC_API_KEY   your key
  VIBEFINDER_MODEL    defaults to claude-opus-5-5
  VIBEFINDER_OFFLINE  set to 1 to force the offline path
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

log = logging.getLogger("vibefinder.llm")

DEFAULT_MODEL = "claude-opus-5-5"
ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Minimal .env loader (KEY=value lines) so we don't need another dependency."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class LLMError(Exception):
    """Raised when the model call fails, is refused, or returns unusable output."""


class ClaudeLLM:
    def __init__(self, model: Optional[str] = None):
        import anthropic  # imported lazily so offline mode never needs the package

        self._anthropic = anthropic
        self.client = anthropic.Anthropic(max_retries=2, timeout=60.0)
        self.model = model or os.environ.get("VIBEFINDER_MODEL", DEFAULT_MODEL)
        self.name = f"claude ({self.model})"

    def _text(self, response) -> str:
        if response.stop_reason == "refusal":
            raise LLMError("model refused the request")
        if response.stop_reason == "max_tokens":
            raise LLMError("model output was cut off (max_tokens)")
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        if not text:
            raise LLMError("model returned no text")
        return text

    def _call(self, **kwargs):
        try:
            return self.client.messages.create(model=self.model, **kwargs)
        except self._anthropic.APIConnectionError as e:
            raise LLMError(f"connection error: {e}") from e
        except self._anthropic.RateLimitError as e:
            raise LLMError("rate limited") from e
        except self._anthropic.APIStatusError as e:
            raise LLMError(f"API error {e.status_code}") from e

    def json(self, system: str, user: str, schema: dict, max_tokens: int = 2000) -> dict:
        """One call that must return JSON matching `schema` (structured outputs)."""
        response = self._call(
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
        )
        try:
            return json.loads(self._text(response))
        except json.JSONDecodeError as e:
            raise LLMError("model returned invalid JSON") from e

    def write(self, system: str, user: str, max_tokens: int = 4000) -> str:
        """One free-text generation call."""
        response = self._call(
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": "medium"},
        )
        return self._text(response)


def get_llm(force_offline: bool = False):
    """Return a ClaudeLLM if a key is configured, otherwise None (offline mode)."""
    load_dotenv()
    if force_offline or os.environ.get("VIBEFINDER_OFFLINE") == "1":
        return None
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        log.info("No ANTHROPIC_API_KEY found: running offline.")
        return None
    try:
        return ClaudeLLM()
    except ImportError:
        log.warning("anthropic package not installed: running offline.")
        return None
