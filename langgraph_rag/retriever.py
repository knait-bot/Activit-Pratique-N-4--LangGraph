from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


TOKEN_RE = re.compile(r"[a-zA-ZÀ-ÿ0-9_']+")


@dataclass(frozen=True)
class RetrievedDocument:
    title: str
    content: str
    score: float


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


def _split_markdown_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title = "Introduction"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line.removeprefix("## ").strip()
            current_lines = []
        elif not line.startswith("# "):
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))
    return [(title, content) for title, content in sections if content]


@lru_cache(maxsize=1)
def load_documents() -> tuple[tuple[str, str], ...]:
    path = Path(__file__).with_name("knowledge_base.md")
    return tuple(_split_markdown_sections(path.read_text(encoding="utf-8")))


def retrieve_documents(question: str, limit: int = 3) -> list[RetrievedDocument]:
    query_tokens = tokenize(question)
    ranked: list[RetrievedDocument] = []

    for title, content in load_documents():
        doc_tokens = tokenize(f"{title}\n{content}")
        overlap = query_tokens & doc_tokens
        score = len(overlap) / max(len(query_tokens), 1)
        if score > 0:
            ranked.append(RetrievedDocument(title=title, content=content, score=score))

    ranked.sort(key=lambda doc: doc.score, reverse=True)
    return ranked[:limit]
