"""
Guardrails: plain-logic checks that limit what the system accepts and returns.

Input guardrails run before any model call:
  * empty or overly long requests
  * prompt-injection attempts ("ignore previous instructions", "system prompt" ...)
  * off-topic requests (nothing music-related in the text)

Output guardrails run on every generated answer:
  * every song title the answer names must exist in the catalog
  * the answer must mention at least one of the songs we actually retrieved
  * no secrets (API keys) may be echoed back
"""

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from src.retriever import KnowledgeBase, contains_phrase

MAX_INPUT_CHARS = 400

INJECTION_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above|earlier) (instructions|rules|prompts?)",
    r"disregard (all |the )?(previous|prior|above) ",
    r"system prompt",
    r"developer mode",
    r"you are now",
    r"jailbreak",
    r"reveal (your|the) (instructions|prompt|rules|key)",
    r"api[_ ]?key",
    r"print (your|the) (instructions|prompt)",
    r"pretend (to be|you are)",
]

MUSIC_WORDS = {
    "song", "songs", "music", "playlist", "track", "tracks", "listen", "listening",
    "vibe", "vibes", "beat", "beats", "tune", "tunes", "album", "artist", "band",
    "recommend", "recommendation", "jam", "jams", "sound", "sounds", "mix",
    "play", "hear", "dj", "radio", "singer", "genre",
}

SECRET_PATTERN = re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}")


@dataclass
class GuardResult:
    ok: bool
    rule: Optional[str] = None
    message: str = ""


def check_input(text: str, kb: KnowledgeBase) -> GuardResult:
    """Decide whether a request is safe and in scope before doing any work."""
    if text is None or not text.strip():
        return GuardResult(False, "empty", "Tell me what you'd like to hear, e.g. 'chill songs for studying'.")
    if len(text) > MAX_INPUT_CHARS:
        return GuardResult(False, "too_long", f"Please keep requests under {MAX_INPUT_CHARS} characters.")
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return GuardResult(False, "prompt_injection",
                               "I can only help with music recommendations, and I can't change my instructions.")
    words = set(re.findall(r"[a-z]+", lowered))
    if words & MUSIC_WORDS or kb.search(text, k=1):
        return GuardResult(True)
    return GuardResult(False, "off_topic",
                       "I'm a music recommender, so I can only help with songs, moods and activities to soundtrack.")


def titles_mentioned(answer: str, catalog_titles: Iterable[str]) -> List[str]:
    """Catalog titles that appear in the answer text."""
    return [t for t in catalog_titles if contains_phrase(answer, t)]


def claimed_titles(answer: str) -> List[str]:
    """Things the answer presents as song titles. The generator is told to **bold** titles only."""
    return [f.strip() for f in re.findall(r"\*\*([^*]{2,60})\*\*", answer)]


def check_output(answer: str, catalog_names: List[str], recommended_titles: List[str]) -> GuardResult:
    """Block hallucinated songs, answers that ignore the evidence, and leaked secrets.

    catalog_names: every title and artist in the catalog (the only names an answer may highlight).
    """
    if not answer or not answer.strip():
        return GuardResult(False, "empty_output", "The model returned nothing.")
    if SECRET_PATTERN.search(answer):
        return GuardResult(False, "secret_leak", "The answer contained something that looks like an API key.")
    known = {t.lower() for t in catalog_names}

    def is_known(claim: str) -> bool:
        claim = claim.lower().strip(" .,:;!")
        if claim in known:
            return True
        # allow "Title by Artist"
        return " by " in claim and all(part.strip() in known for part in claim.split(" by ", 1))

    unknown = [c for c in claimed_titles(answer) if not is_known(c)]
    if unknown:
        return GuardResult(False, "hallucinated_title", f"Answer named songs not in the catalog: {unknown}")
    if not titles_mentioned(answer, recommended_titles):
        return GuardResult(False, "ungrounded", "Answer did not mention any retrieved song.")
    return GuardResult(True)
