# src/persona_manager.py — bilingual, synced with locales.py
"""Fusion layer: combines Streams A, B, C1, C2 into
a persona vector and generates bilingual prompts."""

import json
import logging
import shutil
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
from spacy.cli.download import download

from src.explicit_preferences import ExplicitPreferenceTracker
from src.fuzzy_memory import KeywordMemory, SemanticCloud
from src.implicit_preferences import ImplicitPreferenceTracker
from src.locales import EN, RU
from src.style_surface import SurfaceStyleTracker

logger = logging.getLogger(__name__)

LOCALES = {"ru": RU, "en": EN}


class PersonaManagerError(Exception):
    """Custom exception for PersonaManager errors."""

    pass


class PersonaManager:
    """Manages the full persona: semantic cloud, surface style, and preferences.

    Bilingual: generates prompts in Russian (ru) or English (en) via locales.py.

    Fusion weights (base):
        Stream B (surface style):  0.3 — weak signal, user's own writing style
        Stream C1 (explicit):      0.5 — user said it directly, highest trust
        Stream C2 (implicit):      0.2 — inferred from reactions, lowest trust

    Adaptive weighting:
        If C2 accumulates |value| > 0.7 on any axis, C2 weight for that axis
        rises to 0.5 (strong signal from repeated behavior), taken from B.

    Style invariance:
        Stream B and Stream C use cumulative averaging instead of EMA.
        Style is assumed invariant to dialog order. Content (Stream A)
        and keyword memory retain time-dependent decay (EMA, LRU).
    """

    FUSION_WEIGHTS = {
        "surface": 0.3,
        "explicit": 0.5,
        "implicit": 0.2,
    }
    C2_BOOST_THRESHOLD = 0.7
    C2_BOOSTED_WEIGHT = 0.5
    MIN_DIALOGS_FOR_BOOST = 3

    AXIS_EMOTIONALITY = "emotionality"
    AXIS_FACTUAL = "factual_accuracy"
    AXIS_VERBOSITY = "verbosity"
    AXIS_FIGURATIVENESS = "figurativeness"
    AXIS_DISAGREEMENT = "disagreement"
    AXIS_COMFORT = "comfort"
    AXIS_MODEL_RESISTANCE = "model_resistance"
    AXIS_COMPLEXITY = "complexity"

    VALID_AXES = frozenset(
        [
            AXIS_EMOTIONALITY,
            AXIS_FACTUAL,
            AXIS_VERBOSITY,
            AXIS_FIGURATIVENESS,
            AXIS_DISAGREEMENT,
            AXIS_COMFORT,
            AXIS_MODEL_RESISTANCE,
            AXIS_COMPLEXITY,
        ]
    )

    AXIS_ORDER = [
        AXIS_EMOTIONALITY,
        AXIS_FACTUAL,
        AXIS_VERBOSITY,
        AXIS_FIGURATIVENESS,
        AXIS_DISAGREEMENT,
        AXIS_COMFORT,
        AXIS_MODEL_RESISTANCE,
        AXIS_COMPLEXITY,
    ]

    MAX_STYLE_WEIGHT = 100.0
    MAX_PREF_WEIGHT = 100.0
    CURRENT_VERSION = 4

    def __init__(
        self,
        persona_path: str | None = None,
        model_path: str | None = None,
        encoder: SentenceTransformer | None = None,
        nlp: spacy.language.Language | None = None,
        persist: bool = True,
        lang: str = "en",
    ):
        if lang not in LOCALES:
            raise ValueError(f"Unsupported language: {lang}. Use 'ru' or 'en'.")
        self.lang = lang
        self.L = LOCALES[lang]

        if persona_path is None:
            persona_path = str(
                Path(__file__).parent.parent / "data" / "persona_core.json"
            )

        self.persona_path = Path(persona_path) if persist else None
        self._persist = persist

        if encoder is not None:
            self._encoder = encoder
        else:
            try:
                if model_path is None:
                    model_path = "models/e5-large"
                self._encoder = SentenceTransformer(model_path)
            except Exception as e:
                logger.error(f"Failed to load encoder: {e}")
                raise PersonaManagerError(f"Encoder initialization failed: {e}")

        # spaCy: загружаем модель под текущий язык
        if nlp is not None:
            self._nlp = nlp
        else:
            self._nlp = self._load_spacy_model(lang)

        self.fuzzy_memory = SemanticCloud(model=self._encoder, nlp=self._nlp)
        self.keyword_memory = KeywordMemory(self.fuzzy_memory)
        self.style_tracker = SurfaceStyleTracker(nlp=self._nlp)
        self.explicit_tracker = ExplicitPreferenceTracker(model=self._encoder)
        self.implicit_tracker = ImplicitPreferenceTracker(alpha=0.3)

        self.preferences: dict[str, float] = dict.fromkeys(self.VALID_AXES, 0.0)

        self._style_sum: dict[str, float] | None = None
        self._style_weight: float = 0.0
        self._pref_sum: dict[str, float] | None = None
        self._pref_weight: float = 0.0

        self._dialog_count: int = 0
        self._last_fusion: dict[str, float] | None = None
        self._error_count: int = 0

        if persist:
            self._load()
        else:
            logger.info("Persistence disabled, starting fresh")

    @staticmethod
    def _load_spacy_model(lang: str) -> spacy.language.Language:
        """Load spaCy model for the given language. Falls back to ru if en fails."""
        model_map = {
            "ru": "ru_core_news_sm",
            "en": "en_core_web_sm",
        }
        model_name = model_map.get(lang, "ru_core_news_sm")
        try:
            return spacy.load(model_name)
        except OSError:
            logger.warning(f"{model_name} not found, attempting download...")
            download(model_name)
            return spacy.load(model_name)

    def set_language(self, lang: str) -> None:
        """Switch output language at runtime.
        Invalidates prompt cache and reloads spaCy model."""
        if lang not in LOCALES:
            raise ValueError(f"Unsupported language: {lang}")
        self.lang = lang
        self.L = LOCALES[lang]
        self._nlp = self._load_spacy_model(lang)
        self.style_tracker = SurfaceStyleTracker(nlp=self._nlp)
        self._cached_prompt.cache_clear()
        logger.info(f"Language switched to {lang}")

    # ─── validation, save, load, reset ───

    def _validate_state(self) -> bool:
        try:
            for axis in self.VALID_AXES:
                value = self.preferences.get(axis, 0.0)
                if (
                    not isinstance(value, (int, float))
                    or np.isnan(value)
                    or np.isinf(value)
                ):
                    logger.error(f"Invalid preference value for {axis}: {value}")
                    return False
                if abs(value) > 1.0:
                    logger.warning(f"Preference {axis} out of range: {value}, clipping")
                    self.preferences[axis] = np.clip(value, -1.0, 1.0)
            if self._style_weight < 0 or self._pref_weight < 0:
                logger.error("Negative cumulative weight")
                return False
            return True
        except Exception as e:
            logger.error(f"State validation failed: {e}")
            return False

    def save(self) -> bool:
        if not self._persist or self.persona_path is None:
            return True
        try:
            self.persona_path.parent.mkdir(parents=True, exist_ok=True)
            if self.persona_path.exists():
                backup_path = self.persona_path.with_suffix(".json.bak")
                shutil.copy2(self.persona_path, backup_path)
            data = {
                "version": self.CURRENT_VERSION,
                "updated_at": datetime.now().isoformat(),
                "lang": self.lang,
                "statistics": {
                    "dialog_count": self._dialog_count,
                    "error_count": self._error_count,
                },
                "semantic_cloud": self.fuzzy_memory.to_dict(),
                "surface_style": {
                    "cumulative_sum": self._style_sum,
                    "cumulative_weight": min(self._style_weight, self.MAX_STYLE_WEIGHT),
                },
                "preferences": dict(self.preferences),
                "preferences_cumulative": {
                    "sum": self._pref_sum,
                    "weight": min(self._pref_weight, self.MAX_PREF_WEIGHT),
                },
                "keyword_memory": self.keyword_memory.to_dict(),
            }
            temp_path = self.persona_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path.replace(self.persona_path)
            logger.info(f"Saved persona to {self.persona_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save persona: {e}")
            self._error_count += 1
            return False

    def reset(self) -> None:
        self.fuzzy_memory.semantic_cloud = None
        self.implicit_tracker.inferred_vector = None
        self._style_sum = None
        self._style_weight = 0.0
        self._pref_sum = None
        self._pref_weight = 0.0
        self._dialog_count = 0
        self._last_fusion = None
        for axis in self.VALID_AXES:
            self.preferences[axis] = 0.0
        self._cached_prompt.cache_clear()
        logger.info("Persona state reset")

    def _load(self) -> bool:
        if self.persona_path is None or not self.persona_path.exists():
            logger.info("No existing persona file found, starting fresh")
            return True
        try:
            with open(self.persona_path, encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                return True
            version = data.get("version", 0)
            if version < 1:
                logger.warning(f"Unsupported version {version}, starting fresh")
                return True
            saved_lang = data.get("lang", "ru")
            if saved_lang != self.lang:
                logger.info(
                    f"Switching language from {self.lang} to saved {saved_lang}"
                )
                self.lang = saved_lang
                self.L = LOCALES[saved_lang]
                self._nlp = self._load_spacy_model(saved_lang)
                self.style_tracker = SurfaceStyleTracker(nlp=self._nlp)
            stats = data.get("statistics", {})
            self._dialog_count = stats.get("dialog_count", 0)
            self._error_count = stats.get("error_count", 0)
            cloud_data = data.get("semantic_cloud", {})
            if cloud_data.get("cloud") is not None:
                try:
                    self.fuzzy_memory = SemanticCloud.from_dict(
                        cloud_data, model=self._encoder, nlp=self._nlp
                    )
                except Exception as e:
                    logger.error(f"Failed to restore semantic cloud: {e}")
            style_data = data.get("surface_style", {})
            if style_data:
                self._style_sum = style_data.get("cumulative_sum")
                self._style_weight = min(
                    style_data.get("cumulative_weight", 0.0), self.MAX_STYLE_WEIGHT
                )
            prefs = data.get("preferences", {})
            for axis in self.VALID_AXES:
                if axis in prefs:
                    self.preferences[axis] = np.clip(float(prefs[axis]), -1.0, 1.0)
            pref_cum = data.get("preferences_cumulative", {})
            if pref_cum:
                self._pref_sum = pref_cum.get("sum")
                self._pref_weight = min(
                    pref_cum.get("weight", 0.0), self.MAX_PREF_WEIGHT
                )
            if "keyword_memory" in data:
                try:
                    self.keyword_memory = KeywordMemory.from_dict(
                        data["keyword_memory"], self.fuzzy_memory
                    )
                except Exception as e:
                    logger.error(f"Failed to restore keyword memory: {e}")
                    self.keyword_memory = KeywordMemory(self.fuzzy_memory)
            else:
                self.keyword_memory = KeywordMemory(self.fuzzy_memory)
            if not self._validate_state():
                logger.warning("State validation failed after load, resetting")
                self.reset()
                return False
            logger.info(
                f"Loaded persona from {self.persona_path}"
                f" (v{version}, lang={self.lang})"
            )
            return True
        except json.JSONDecodeError:
            logger.warning("Corrupted persona file, attempting backup restore")
            return self._restore_from_backup()
        except Exception as e:
            logger.warning(f"Failed to load persona: {e}, starting fresh")
            return True

    def _restore_from_backup(self) -> bool:
        if self.persona_path is None:
            return True
        backup_path = self.persona_path.with_suffix(".json.bak")
        if backup_path.exists():
            try:
                shutil.copy2(backup_path, self.persona_path)
                return self._load()
            except Exception as e:
                logger.error(f"Backup restore failed: {e}")
        logger.warning("No backup available, starting fresh")
        return True

    # ─── update cycle ───

    def update_after_dialog(
        self, dialog: list[dict[str, Any]], update_memory: bool = True
    ) -> bool:
        try:
            if not dialog:
                return True
            user_messages = [m["content"] for m in dialog if m.get("role") == "user"]
            if not user_messages:
                return True
            if update_memory:
                for msg in user_messages:
                    self.fuzzy_memory.process_message(msg)
                for i in range(len(dialog) - 1):
                    if (
                        dialog[i].get("role") == "user"
                        and dialog[i + 1].get("role") == "assistant"
                    ):
                        self.keyword_memory.add_pair(
                            dialog[i]["content"], dialog[i + 1]["content"]
                        )
            b_features = self.style_tracker.extract(user_messages)
            if self._style_sum is None:
                self._style_sum = dict.fromkeys(b_features, 0.0)
            for key, value in b_features.items():
                self._style_sum[key] = self._style_sum.get(key, 0.0) + value
            self._style_weight = min(self._style_weight + 1.0, self.MAX_STYLE_WEIGHT)
            current_style = (
                {k: v / self._style_weight for k, v in self._style_sum.items()}
                if self._style_weight > 0
                else None
            )
            c1_vector = dict.fromkeys(self.VALID_AXES, 0.0)
            for msg in user_messages:
                anchors = self.explicit_tracker.detect_anchors(msg)
                for axis in c1_vector:
                    if abs(anchors.get(axis, 0.0)) > abs(c1_vector[axis]):
                        c1_vector[axis] = anchors.get(axis, 0.0)
            for i in range(len(dialog) - 1):
                if (
                    dialog[i].get("role") == "assistant"
                    and dialog[i + 1].get("role") == "user"
                ):
                    signals = self.implicit_tracker.analyze_reaction(
                        dialog[i]["content"], dialog[i + 1]["content"]
                    )
                    self.implicit_tracker.update_inferred_preferences(signals)
            c2_vector = self.implicit_tracker.get_inferred_vector() or dict.fromkeys(
                self.VALID_AXES, 0.0
            )
            b_scaled = self._scale_surface_to_preferences(current_style)
            dialog_signal = {}
            for axis in self.VALID_AXES:
                w_b = self.FUSION_WEIGHTS["surface"]
                w_c1 = self.FUSION_WEIGHTS["explicit"]
                w_c2 = self.FUSION_WEIGHTS["implicit"]
                c2_value = c2_vector.get(axis, 0.0)
                if (
                    abs(c2_value) > self.C2_BOOST_THRESHOLD
                    and self._dialog_count >= self.MIN_DIALOGS_FOR_BOOST
                ):
                    w_c2 = min(
                        self.C2_BOOSTED_WEIGHT,
                        w_c2 + 0.1 * (self._dialog_count - self.MIN_DIALOGS_FOR_BOOST),
                    )
                    w_b = max(
                        0.0,
                        self.FUSION_WEIGHTS["surface"]
                        - (w_c2 - self.FUSION_WEIGHTS["implicit"]),
                    )
                dialog_signal[axis] = (
                    w_b * b_scaled.get(axis, 0.0)
                    + w_c1 * c1_vector.get(axis, 0.0)
                    + w_c2 * c2_value
                )
            self._last_fusion = dict(dialog_signal)
            if self._pref_sum is None:
                self._pref_sum = dict.fromkeys(self.VALID_AXES, 0.0)
            for axis in self.VALID_AXES:
                self._pref_sum[axis] = (
                    self._pref_sum.get(axis, 0.0) + dialog_signal[axis]
                )
            self._pref_weight = min(self._pref_weight + 1.0, self.MAX_PREF_WEIGHT)
            if self._pref_weight > 0:
                for axis in self.VALID_AXES:
                    self.preferences[axis] = np.clip(
                        self._pref_sum[axis] / self._pref_weight, -1.0, 1.0
                    )
            self._dialog_count += 1
            if not self._validate_state():
                logger.error("State validation failed after update")
                return False
            if self._persist:
                self.save()
            logger.info(
                f"Updated preferences (dialog #{self._dialog_count}): "
                f"{ {k: round(v, 3) for k, v in self.preferences.items()} }"
            )
            return True
        except Exception as e:
            logger.error(f"Critical error in update_after_dialog: {e}")
            self._error_count += 1
            return False

    def _scale_surface_to_preferences(
        self, surface_ema: dict[str, float] | None
    ) -> dict[str, float]:
        if surface_ema is None:
            return dict.fromkeys(self.VALID_AXES, 0.0)
        emphasis = surface_ema.get("emphasis_ratio", 0.0)
        evaluative = surface_ema.get("evaluative_ratio", 0.0)
        first_person = surface_ema.get("first_person_ratio", 0.0)
        hedging = surface_ema.get("hedging_ratio", 0.0)
        question_ratio = surface_ema.get("question_ratio", 0.0)
        declarative = surface_ema.get("declarative_ratio", 0.0)
        imperative = surface_ema.get("imperative_ratio", 0.0)
        fig_ratio = surface_ema.get("figurative_markers_ratio", 0.0)
        adj_density = surface_ema.get("adjective_density", 0.0)
        avg_sent_len = surface_ema.get("avg_sentence_length", 0.0)
        fog_index = surface_ema.get("fog_index", 8.0)
        scaled = {
            self.AXIS_EMOTIONALITY: float(
                np.clip(
                    emphasis * 80
                    + evaluative * 60
                    + first_person * 10
                    - hedging * 25
                    + declarative * 0.5
                    - 0.3,
                    -1.0,
                    1.0,
                )
            ),
            self.AXIS_FACTUAL: float(
                np.clip(
                    (1.0 - question_ratio) * 1.5 - hedging * 40 + 0.1,
                    -1.0,
                    1.0,
                )
            ),
            self.AXIS_VERBOSITY: 0.0,
            self.AXIS_FIGURATIVENESS: float(
                np.clip(
                    fig_ratio / 0.05 + adj_density / 60 + avg_sent_len / 12 - 0.5,
                    -1.0,
                    1.0,
                )
            ),
            self.AXIS_DISAGREEMENT: 0.0,
            self.AXIS_COMFORT: float(
                np.clip(
                    hedging * 15
                    + avg_sent_len * 0.03
                    - imperative * 20
                    - first_person * 15
                    - 0.05,
                    -1.0,
                    1.0,
                )
            ),
            self.AXIS_MODEL_RESISTANCE: float(
                np.clip(
                    emphasis * 40 + declarative * 1.5 - hedging * 25 + 0.15,
                    0.0,
                    1.0,
                )
            ),
            self.AXIS_COMPLEXITY: float(
                np.clip(
                    (fog_index - 8.0) / 4.0,
                    -1.0,
                    1.0,
                )
            ),
        }
        for axis, value in scaled.items():
            if np.isnan(value) or np.isinf(value):
                logger.warning(f"NaN/Inf in scaled surface for {axis}, setting to 0")
                scaled[axis] = 0.0
        return scaled

    # ─── prompt generation (bilingual) ───

    def _get_prompt_key(self, axis: str, value: float) -> str | None:
        """Map axis + value range to a locales.py prompt key."""
        ranges = {
            self.AXIS_EMOTIONALITY: [
                (-1.0, -0.7, "prompt_emotionality_low"),
                (-0.7, -0.1, "prompt_emotionality_mid_low"),
                (-0.1, 0.3, "prompt_emotionality_mid"),
                (0.3, 0.7, "prompt_emotionality_mid_high"),
                (0.7, 1.0, "prompt_emotionality_high"),
            ],
            self.AXIS_FACTUAL: [
                (-1.0, -0.5, "prompt_factual_low"),
                (-0.5, -0.1, "prompt_factual_mid_low"),
                (-0.1, 0.3, "prompt_factual_mid"),
                (0.3, 0.7, "prompt_factual_mid_high"),
                (0.7, 1.0, "prompt_factual_high"),
            ],
            self.AXIS_VERBOSITY: [
                (-1.0, -0.5, "prompt_verbosity_low"),
                (-0.5, -0.2, "prompt_verbosity_mid_low"),
                (-0.2, 0.2, "prompt_verbosity_mid"),
                (0.2, 0.5, "prompt_verbosity_mid_high"),
                (0.5, 1.0, "prompt_verbosity_high"),
            ],
            self.AXIS_FIGURATIVENESS: [
                (-1.0, -0.5, "prompt_figurativeness_low"),
                (-0.5, -0.1, "prompt_figurativeness_mid_low"),
                (-0.1, 0.3, "prompt_figurativeness_mid"),
                (0.3, 0.7, "prompt_figurativeness_mid_high"),
                (0.7, 1.0, "prompt_figurativeness_high"),
            ],
            self.AXIS_DISAGREEMENT: [
                (-1.0, -0.5, "prompt_disagreement_low"),
                (-0.5, -0.2, "prompt_disagreement_mid_low"),
                (-0.2, 0.2, "prompt_disagreement_mid"),
                (0.2, 0.5, "prompt_disagreement_mid_high"),
                (0.5, 1.0, "prompt_disagreement_high"),
            ],
            self.AXIS_COMFORT: [
                (-1.0, -0.5, "prompt_comfort_low"),
                (-0.5, -0.1, "prompt_comfort_mid_low"),
                (-0.1, 0.3, "prompt_comfort_mid"),
                (0.3, 0.7, "prompt_comfort_mid_high"),
                (0.7, 1.0, "prompt_comfort_high"),
            ],
            self.AXIS_MODEL_RESISTANCE: [
                (0.0, 0.2, "prompt_model_resistance_low"),
                (0.2, 0.4, "prompt_model_resistance_mid_low"),
                (0.4, 0.7, "prompt_model_resistance_mid_high"),
                (0.7, 1.0, "prompt_model_resistance_high"),
            ],
            self.AXIS_COMPLEXITY: [
                (-1.0, -0.5, "prompt_complexity_low"),
                (-0.5, -0.1, "prompt_complexity_mid_low"),
                (-0.1, 0.3, "prompt_complexity_mid"),
                (0.3, 0.7, "prompt_complexity_mid_high"),
                (0.7, 1.0, "prompt_complexity_high"),
            ],
        }
        axis_ranges = ranges.get(axis, [])
        for low, high, key in axis_ranges:
            if low <= value <= high:
                return key
        return None

    def _get_label(self, axis: str, value: float, lang: str | None = None) -> str:
        """Get human-readable label for axis value from locales."""
        key = self._get_prompt_key(axis, value)
        L = LOCALES.get(lang, self.L) if lang else self.L
        if key and key in L:
            return L[key]
        return "neutral" if (lang or self.lang) == "en" else "нейтрально"

    @lru_cache(maxsize=200)  # noqa: B019
    def _cached_prompt(
        self, preferences_tuple: tuple[float, ...], question_hash: int, lang: str
    ) -> str:
        """Generate full persona prompt from cached preferences.
        Lang is part of cache key.

        NOTE: lru_cache on instance method is generally discouraged due to potential
        memory leaks (self stored in cache key). However, PersonaManager is a singleton
        in Streamlit (managed by @st.cache_resource), so only one self instance exists.
        Acceptable for MVP. Refactor to @staticmethod if scaling to multiple instances.
        """
        L = LOCALES[lang]
        parts = []
        for i, axis in enumerate(self.AXIS_ORDER):
            value = preferences_tuple[i]
            label = self._get_label(axis, value, lang=lang)
            parts.append(f"- {label}")
        frame = L.get("prompt_frame_auto", "[Style instructions — auto]")
        close = L.get("prompt_frame_close", "[/Instructions]")
        return f"{frame}\n" + "\n".join(parts) + f"\n{close}"

    def get_persona_prompt(
        self,
        current_question: str | None = None,
        lang: str | None = None,
        use_memory: bool = True,
    ) -> str:
        """Generate persona prompt in specified language (or current if None)."""
        try:
            if lang and lang != self.lang:
                self.set_language(lang)

            preferences_tuple = tuple(
                self.preferences[axis] for axis in self.AXIS_ORDER
            )
            question_hash = hash(current_question) if current_question else 0
            base_prompt = self._cached_prompt(
                preferences_tuple, question_hash, self.lang
            )
            parts = base_prompt.split("\n")

            if current_question:
                if use_memory and self.keyword_memory is not None:
                    try:
                        memory_keywords = self.keyword_memory.query(current_question)
                        if memory_keywords:
                            prefix = self.L.get(
                                "prompt_memory_prefix", "[Memory] Previously discussed:"
                            )
                            suffix = self.L.get(
                                "prompt_memory_suffix", "Use as context. [/Memory]"
                            )
                            context = (
                                f"{prefix} {', '.join(memory_keywords[:10])}. {suffix}"
                            )
                            parts.insert(0, context)
                    except Exception as e:
                        logger.error(f"Keyword memory query failed: {e}")

            return "\n".join(parts)
        except Exception as e:
            logger.error(f"Error generating persona prompt: {e}")
            fallback = self.L.get("prompt_frame_auto", "[Style instructions — auto]")
            close = self.L.get("prompt_frame_close", "[/Instructions]")
            ret = f"{fallback}\n- "
            f"{self.L.get('emotionality_label_0', 'neutral')}\n{close}"
            return ret

    # ─── stats ───

    def get_persona_stats(self) -> dict[str, Any]:
        return {
            "dialog_count": self._dialog_count,
            "error_count": self._error_count,
            "style_weight": self._style_weight,
            "pref_weight": self._pref_weight,
            "preferences": dict(self.preferences),
            "last_fusion": self._last_fusion,
            "has_cloud": self.fuzzy_memory.semantic_cloud is not None,
            "lang": self.lang,
        }

    def __repr__(self) -> str:
        ret = f"PersonaManager(dialogs={self._dialog_count},"
        f"errors={self._error_count}, lang={self.lang},"
        f"persist={self._persist})"
        return ret
