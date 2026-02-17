from __future__ import annotations

import re
from collections import Counter


class SummaryService:
    STOPWORDS = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "vous",
        "dans",
        "pour",
        "avec",
        "une",
        "des",
        "les",
        "est",
        "sur",
    }

    def summarize(self, text: str, max_sentences: int = 5) -> str:
        cleaned = re.sub(r"\s+", " ", text or "").strip()
        if not cleaned:
            return "Résumé indisponible : ajoutez un résumé personnalisé."

        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        words = re.findall(r"[\w']+", cleaned.lower())
        freqs = Counter(w for w in words if len(w) > 3 and w not in self.STOPWORDS)

        scored: list[tuple[int, float]] = []
        for idx, sentence in enumerate(sentences):
            s_words = re.findall(r"[\w']+", sentence.lower())
            score = sum(freqs.get(w, 0) for w in s_words)
            scored.append((idx, score))

        top_indexes = sorted(
            [idx for idx, _ in sorted(scored, key=lambda row: row[1], reverse=True)[:max_sentences]]
        )
        return " ".join(sentences[idx] for idx in top_indexes)
