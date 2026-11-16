"""
Retrieval over the custom knowledge base in knowledge/*.md.

Each "## heading" section is one chunk. A chunk has a kind (genre, mood or
activity, taken from the file name), a name, optional metadata lines
("family: pop", "aliases: kpop, korean pop", "energy: 0.8") and free text.

Retrieval is deliberately simple and explainable: a chunk scores high when its
name or one of its aliases appears in the query as a phrase, plus a small bonus
for every word the query shares with the chunk text.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
KIND_BY_FILE = {"genres": "genre", "moods": "mood", "activities": "activity"}
STOPWORDS = {
    "a", "an", "and", "the", "for", "to", "of", "in", "on", "me", "my", "i", "some",
    "with", "that", "is", "it", "but", "or", "be", "can", "you", "songs", "song",
    "music", "want", "like", "give", "please", "something", "too", "not", "no",
}


def tokenize(text: str) -> List[str]:
    """Lowercase words (letters, digits, &, -) without stopwords."""
    return [w for w in re.findall(r"[a-z0-9&\-]+", text.lower()) if w not in STOPWORDS]


def contains_phrase(text: str, phrase: str) -> bool:
    """True if `phrase` appears in `text` as whole words (case-insensitive)."""
    pattern = r"(?<![a-z0-9\-])" + re.escape(phrase.lower()) + r"(?![a-z0-9\-])"
    return re.search(pattern, text.lower()) is not None


@dataclass
class Chunk:
    id: str
    kind: str
    name: str
    text: str
    meta: Dict[str, str] = field(default_factory=dict)

    @property
    def aliases(self) -> List[str]:
        raw = self.meta.get("aliases", "")
        return [a.strip().lower() for a in raw.split(",") if a.strip()]

    @property
    def family(self) -> Optional[str]:
        return self.meta.get("family")

    def number(self, key: str) -> Optional[float]:
        try:
            return float(self.meta[key])
        except (KeyError, ValueError):
            return None


@dataclass
class Hit:
    chunk: Chunk
    score: float
    matched: Optional[str]  # the phrase that matched, if any


class KnowledgeBase:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks

    @classmethod
    def load(cls, directory: Path = KNOWLEDGE_DIR) -> "KnowledgeBase":
        chunks: List[Chunk] = []
        for path in sorted(Path(directory).glob("*.md")):
            kind = KIND_BY_FILE.get(path.stem, path.stem)
            for section in path.read_text(encoding="utf-8").split("\n## ")[1:]:
                lines = section.strip().splitlines()
                name = lines[0].strip().lower()
                meta, body = {}, []
                for line in lines[1:]:
                    m = re.match(r"^([a-z]+):\s*(.*)$", line.strip())
                    if m and not body:
                        meta[m.group(1)] = m.group(2).strip()
                    elif line.strip():
                        body.append(line.strip())
                chunks.append(Chunk(f"{kind}:{name}", kind, name, " ".join(body), meta))
        return cls(chunks)

    @classmethod
    def catalog_only(cls, songs: List[Dict]) -> "KnowledgeBase":
        """Baseline without custom notes: only the exact genre/mood labels in the catalog
        (no aliases, no families, no activities). This is how VibeFinder 1.0 understood people."""
        chunks = [Chunk(f"genre:{g}", "genre", g, "") for g in sorted({s["genre"] for s in songs})]
        chunks += [Chunk(f"mood:{m}", "mood", m, "") for m in sorted({s["mood"] for s in songs})]
        return cls(chunks)

    def by_kind(self, kind: str) -> List[Chunk]:
        return [c for c in self.chunks if c.kind == kind]

    def get(self, kind: str, name: str) -> Optional[Chunk]:
        name = (name or "").strip().lower()
        for c in self.by_kind(kind):
            if c.name == name or name in c.aliases:
                return c
        return None

    def family_of(self, kind: str, name: str) -> Optional[str]:
        chunk = self.get(kind, name)
        return chunk.family if chunk else None

    def search(self, query: str, k: int = 5, kinds: Optional[List[str]] = None) -> List[Hit]:
        """Rank chunks for a query. Phrase matches on name/alias dominate."""
        q_tokens = set(tokenize(query))
        hits: List[Hit] = []
        for chunk in self.chunks:
            if kinds and chunk.kind not in kinds:
                continue
            score, matched = 0.0, None
            for phrase in [chunk.name] + chunk.aliases:
                if contains_phrase(query, phrase):
                    # longer phrases are more specific ("night drive" beats "drive")
                    phrase_score = 3.0 + 0.1 * len(phrase)
                    if phrase_score > score:
                        score, matched = phrase_score, phrase
            overlap = q_tokens & set(tokenize(chunk.text))
            score += 0.2 * len(overlap)
            if score > 0.25:
                hits.append(Hit(chunk, round(score, 3), matched))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]

    def best_match(self, query: str, kind: str) -> Optional[Hit]:
        """The strongest *phrase* match of one kind, or None."""
        for hit in self.search(query, k=len(self.chunks), kinds=[kind]):
            if hit.matched:
                return hit
        return None
