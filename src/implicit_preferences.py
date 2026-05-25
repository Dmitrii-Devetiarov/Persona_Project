# src/implicit_preferences.py
"""Stream C2: Inferred preferences from user reactions to model responses.
Bilingual: English (en, default) and Russian (ru).
Markers loaded from locales.py.

Axes covered (5 of 8):
    emotionality, factual_accuracy, verbosity, disagreement, comfort

Axes NOT covered by C2:
    model_resistance — measured in Stream B (surface style) and C1 (explicit)
    complexity — measured in Stream B (fog_index) and C1 (explicit)
    figurativeness — measured in Stream B and C1
"""

import re

from src.locales import EN, RU


class ImplicitPreferenceTracker:
    """Analyzes user follow-ups to model responses for implicit style signals.

    Bilingual: English (en, default) and Russian (ru).
    Marker lists loaded from locales.py, switched via set_language().
    """

    EMOJI_PATTERN = re.compile(
        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
        r"\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
        r"\U00002702-\U000027B0\U000024C2-\U0001F251]"
    )

    def __init__(self, alpha: float = 0.3, lang: str = "en"):
        self.alpha = alpha
        self.inferred_vector: dict[str, float] | None = None
        self.lang = lang
        self.L = EN if lang == "en" else RU
        self._update_markers()

    def set_language(self, lang: str) -> None:
        """Switch marker language."""
        if lang != self.lang:
            self.lang = lang
            self.L = EN if lang == "en" else RU
            self._update_markers()

    def _update_markers(self) -> None:
        """Load marker lists from current locale."""
        self.DISAGREEMENT_MARKERS = self.L.get("implicit_disagreement", [])
        self.CORRECTION_ACCEPTANCE_MARKERS = self.L.get(
            "implicit_correction_acceptance", []
        )
        self.AGREEMENT_MARKERS = self.L.get("implicit_agreement", [])
        self.FACTUAL_DEMAND_MARKERS = self.L.get("implicit_factual_demand", [])
        self.EMPATHY_MARKERS = self.L.get("implicit_empathy", [])
        self.DRY_RESPONSE_MARKERS = self.L.get("implicit_dry_response", [])
        self.POSITIVE_REACTION_MARKERS = self.L.get("implicit_positive_reaction", [])
        self.ELABORATION_REQUEST_MARKERS = self.L.get(
            "implicit_elaboration_request", []
        )

    def _count_tokens(self, text: str) -> int:
        """Quick token count by whitespace."""
        return len(text.split())

    def _has_emoji(self, text: str) -> bool:
        return bool(self.EMOJI_PATTERN.search(text))

    def analyze_reaction(
        self,
        model_response: str,
        user_followup: str,
    ) -> dict[str, float]:
        """Analyze a single reaction pair for implicit signals.

        Args:
            model_response: What the model said.
            user_followup: User's next message after model response.

        Returns:
            Dict with 5 axes, each in [-1, 1] where non-zero = signal detected.
            Axes: emotionality, factual_accuracy, verbosity, disagreement, comfort.
        """
        signals = {
            "emotionality": 0.0,
            "factual_accuracy": 0.0,
            "verbosity": 0.0,
            "disagreement": 0.0,
            "comfort": 0.0,
        }

        resp_tokens = self._count_tokens(model_response)
        followup_tokens = self._count_tokens(user_followup)
        followup_lower = user_followup.lower()
        response_lower = model_response.lower()

        # ── verbosity ──────────────────────────────────────────────
        if resp_tokens > 0:
            ratio = followup_tokens / resp_tokens
            if ratio < 0.15:
                signals["verbosity"] = -0.8
            elif ratio > 5.0:
                signals["verbosity"] = +0.5

        for marker in self.ELABORATION_REQUEST_MARKERS:
            if marker in followup_lower:
                if signals["verbosity"] <= 0:
                    signals["verbosity"] = +0.6
                break

        # ── disagreement ───────────────────────────────────────────
        for marker in self.DISAGREEMENT_MARKERS:
            if marker in followup_lower:
                signals["disagreement"] = +0.8
                break

        if signals["disagreement"] == 0.0:
            for marker in self.AGREEMENT_MARKERS:
                if (
                    followup_lower.strip().startswith(marker)
                    or f", {marker}" in followup_lower
                ):
                    signals["disagreement"] = -0.4
                    break

        # ── factual_accuracy ───────────────────────────────────────
        for marker in self.FACTUAL_DEMAND_MARKERS:
            if marker in followup_lower:
                signals["factual_accuracy"] = +0.8
                break

        # ── emotionality ───────────────────────────────────────────
        model_has_empathy = any(
            marker in response_lower for marker in self.EMPATHY_MARKERS
        )

        user_is_dry = (
            followup_tokens < 8
            or any(marker in followup_lower for marker in self.DRY_RESPONSE_MARKERS)
        ) and not any(
            marker in followup_lower for marker in self.POSITIVE_REACTION_MARKERS
        )

        if model_has_empathy and user_is_dry and not self._has_emoji(user_followup):
            signals["emotionality"] = -0.6
        elif model_has_empathy and self._has_emoji(user_followup):
            signals["emotionality"] = +0.4

        return signals

    def update_inferred_preferences(
        self,
        signals: dict[str, float],
    ) -> dict[str, float]:
        """Update inferred preference vector with new signals.

        Modifies internal state and returns a copy.
        """
        if self.inferred_vector is None:
            self.inferred_vector = dict.fromkeys(signals, 0.0)

        for axis, value in signals.items():
            if value != 0.0:
                self.inferred_vector[axis] = (
                    self.alpha * value + (1 - self.alpha) * self.inferred_vector[axis]
                )

        return self.inferred_vector.copy()

    def get_inferred_vector(self) -> dict[str, float] | None:
        return self.inferred_vector.copy() if self.inferred_vector else None
