# src/implicit_preferences.py
"""Stream C2: Inferred preferences from user reactions to model responses.

Axes (6 total — subset of persona_manager's 8):
    emotionality, factual_accuracy, verbosity,
    figurativeness, disagreement, comfort

Axes NOT covered by C2:
    model_resistance — measured in Stream B (surface style) and C1 (explicit)
    complexity — measured in Stream B (fog_index) and C1 (explicit)
"""

import re
from typing import Optional


class ImplicitPreferenceTracker:
    """Analyzes user follow-ups to model responses for implicit style signals."""

    # Маркеры несогласия пользователя с моделью
    DISAGREEMENT_MARKERS = [
        "нет", "не согласен", "ты не прав", "ты неправ", "ошибся",
        "неверно", "не так", "неправильно", "ты путаешь", "забудь",
        "это не то", "не об этом", "не надо", "прекрати",
    ]

    # Маркеры принятия правки (пользователь согласился, что модель его поправила)
    CORRECTION_ACCEPTANCE_MARKERS = [
        "да, ты прав", "ты прав", "согласен", "точно", "исправь",
        "хорошо, поправлю", "ок, переделай", "ладно, убедил",
        "верно", "действительно", "принято", "понял, исправлю",
        "хорошо, учту", "спасибо за поправку", "ты верно заметил",
        "убедительно", "резонно", "в яблочко", "верно подмечено",
    ]

    # Маркеры явного согласия пользователя (сигнал на негативный полюс disagreement)
    AGREEMENT_MARKERS = [
        "да", "верно", "правильно", "именно", "в точку",
        "продолжай", "хорошо", "отлично", "так и есть",
    ]

    # Маркеры требования фактов
    FACTUAL_DEMAND_MARKERS = [
        "откуда это", "источник", "ты уверен", "уверен ли",
        "подтверди", "докажи", "ссылка", "citation",
        "на чём основано", "откуда данные", "чем подтверждено",
    ]

    # Маркеры эмпатии в ответе модели
    EMPATHY_MARKERS = [
        "понимаю", "сочувствую", "жаль", "мне жаль",
        "соболезную", "держись", "ты справишься", "всё будет хорошо",
        "не переживай", "я понимаю", "это тяжело", "это сложно",
    ]

    # Маркеры сухого ответа пользователя (даже при короткой длине)
    DRY_RESPONSE_MARKERS = [
        "ясно", "понятно", "ок", "окей", "ага", "угу",
        "ладно", "хорошо", "принято",
    ]

    # Маркеры позитивной реакции пользователя
    POSITIVE_REACTION_MARKERS = [
        "спасибо", "отлично", "здорово", "круто", "класс",
        "супер", "благодарю",
    ]

    # Маркеры запроса большей детализации
    ELABORATION_REQUEST_MARKERS = [
        "подробнее", "расскажи подробнее", "распиши", "разверни",
        "продолжи", "дальше", "что ещё", "ещё",
    ]

    EMOJI_PATTERN = re.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF'
        r'\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF'
        r'\U00002702-\U000027B0\U000024C2-\U0001F251]'
    )

    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
        self.inferred_vector: dict[str, float] | None = None

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
            Dict with 6 axes, each in [-1, 1] where non-zero = signal detected.
            Axes: emotionality, factual_accuracy, verbosity,
                  figurativeness, disagreement, comfort.
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
                signals["verbosity"] = -0.8  # пользователь не читал — слишком длинно
            elif ratio > 5.0:
                signals["verbosity"] = +0.5  # пользователь просит ещё

        # Дополнительно: явный запрос детализации
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

        # Сигнал на негативный полюс: пользователь явно соглашается
        if signals["disagreement"] == 0.0:
            for marker in self.AGREEMENT_MARKERS:
                if followup_lower.strip().startswith(marker) or f", {marker}" in followup_lower:
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

        # Сухой ответ: короткий ИЛИ содержит маркеры сухости, но не содержит позитивной реакции
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

        Args:
            signals: Output from analyze_reaction.

        Returns:
            Updated inferred preference vector (copy).
        """
        if self.inferred_vector is None:
            self.inferred_vector = {axis: 0.0 for axis in signals}

        for axis, value in signals.items():
            if value != 0.0:
                self.inferred_vector[axis] = (
                    self.alpha * value
                    + (1 - self.alpha) * self.inferred_vector[axis]
                )

        return self.inferred_vector.copy()

    def get_inferred_vector(self) -> dict[str, float] | None:
        return self.inferred_vector.copy() if self.inferred_vector else None