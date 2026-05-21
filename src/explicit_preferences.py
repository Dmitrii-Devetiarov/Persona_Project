# src/explicit_preferences.py
"""Stream C1: Explicit preference detection via prototype embedding similarity.
Bilingual: English (en, default) and Russian (ru).
Uses prototype texts from locales.py.
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer
from src.locales import RU, EN


class ExplicitPreferenceTracker:
    """Detects explicit style instructions in user messages.

    Bilingual: English (en, default) and Russian (ru).
    Prototypes loaded from locales.py, precomputed at init.
    Single comparison per axis — no phrase list iteration.
    """

    AXES = [
        "emotionality",
        "factual_accuracy",
        "verbosity",
        "figurativeness",
        "model_resistance",
        "comfort",
        "disagreement",
        "complexity",
    ]

    COSINE_THRESHOLD = 0.82

    def __init__(
        self,
        model: SentenceTransformer | None = None,
        lang: str = "en",
    ):
        if model is None:
            raise ValueError(
                "SentenceTransformer model must be provided. "
                "Pass a pre-loaded model to ExplicitPreferenceTracker(model=...)"
            )
        self.encoder = model
        self.lang = lang
        self.L = EN if lang == "en" else RU

        self._prototype_embeddings: dict[str, dict[str, np.ndarray]] = {}
        self._precompute_embeddings()

    def set_language(self, lang: str) -> None:
        """Switch prototype language and recompute embeddings."""
        if lang != self.lang:
            self.lang = lang
            self.L = EN if lang == "en" else RU
            self._prototype_embeddings = {}
            self._precompute_embeddings()

    def _precompute_embeddings(self) -> None:
        """Embed all prototypes from locales once at init or after language switch."""
        locale_keys = {
            "emotionality": ("explicit_emotionality_pos", "explicit_emotionality_neg"),
            "factual_accuracy": ("explicit_factual_pos", "explicit_factual_neg"),
            "verbosity": ("explicit_verbosity_pos", "explicit_verbosity_neg"),
            "figurativeness": ("explicit_figurativeness_pos", "explicit_figurativeness_neg"),
            "model_resistance": ("explicit_model_resistance_pos", "explicit_model_resistance_neg"),
            "comfort": ("explicit_comfort_pos", "explicit_comfort_neg"),
            "disagreement": ("explicit_disagreement_pos", "explicit_disagreement_neg"),
            "complexity": ("explicit_complexity_pos", "explicit_complexity_neg"),
        }
        for axis, (pos_key, neg_key) in locale_keys.items():
            pos_text = self.L.get(pos_key, "")
            neg_text = self.L.get(neg_key, "")
            self._prototype_embeddings[axis] = {
                "positive": self.encoder.encode(f"query: {pos_text}", normalize_embeddings=True) if pos_text else None,
                "negative": self.encoder.encode(f"query: {neg_text}", normalize_embeddings=True) if neg_text else None,
            }

    def detect_anchors(self, user_message: str) -> dict[str, float]:
        """Detect explicit style instructions in a user message.

        Args:
            user_message: Single user message text.

        Returns:
            Dict with 8 axes, each in [-1, 1]:
            positive = user wants more of the trait,
            negative = user wants less,
            0 = no anchor detected.
        """
        msg_embedding = self.encoder.encode(
            f"query: {user_message}",
            normalize_embeddings=True,
        )

        result: dict[str, float] = {}

        for axis in self.AXES:
            pos_emb = self._prototype_embeddings.get(axis, {}).get("positive")
            neg_emb = self._prototype_embeddings.get(axis, {}).get("negative")

            pos_sim = float(np.dot(pos_emb, msg_embedding)) if pos_emb is not None else 0.0
            neg_sim = float(np.dot(neg_emb, msg_embedding)) if neg_emb is not None else 0.0

            if pos_sim > self.COSINE_THRESHOLD and pos_sim > neg_sim:
                result[axis] = pos_sim
            elif neg_sim > self.COSINE_THRESHOLD and neg_sim > pos_sim:
                result[axis] = -neg_sim
            else:
                result[axis] = 0.0

        return result

    def update_explicit_preferences(
        self,
        current_vector: dict[str, float] | None,
        detected_anchors: dict[str, float],
        alpha: float = 0.8,
    ) -> dict[str, float]:
        """Update explicit preference vector with newly detected anchors.

        Args:
            current_vector: Current 8-axis preference vector, or None to start fresh.
            detected_anchors: Output from detect_anchors.
            alpha: Weight for new anchors. High because anchors are explicit instructions.

        Returns:
            Updated preference vector.
        """
        if current_vector is None:
            current_vector = {axis: 0.0 for axis in self.AXES}

        for axis in self.AXES:
            anchor_value = detected_anchors.get(axis, 0.0)
            if anchor_value != 0.0:
                current_vector[axis] = (
                    alpha * anchor_value
                    + (1 - alpha) * current_vector.get(axis, 0.0)
                )

        return current_vector