# src/style_surface.py
"""Stream B: Surface Style Features.
Bilingual: English (en, default) and Russian (ru).
Uses spaCy + syllabreak for syllable counting and Gunning Fog Index.
Markers loaded from locales.py. Graceful degradation to heuristic if syllabreak unavailable.
"""

import re
import statistics
from typing import Optional
import spacy
from src.locales import RU, EN

# ─── syllable counting with graceful degradation ───

_SYLLABLE_COUNTER = None
_SYLLABLE_COUNTER_AVAILABLE = False


def _init_syllable_counter() -> bool:
    """Try to load syllabreak. Returns True if successful."""
    global _SYLLABLE_COUNTER, _SYLLABLE_COUNTER_AVAILABLE
    if _SYLLABLE_COUNTER is not None:
        return _SYLLABLE_COUNTER_AVAILABLE
    try:
        from syllabreak import Syllabreak
        _SYLLABLE_COUNTER = Syllabreak()
        _SYLLABLE_COUNTER_AVAILABLE = True
    except ImportError:
        _SYLLABLE_COUNTER_AVAILABLE = False
    return _SYLLABLE_COUNTER_AVAILABLE


def _count_syllables(word: str, lang: str = "en") -> int:
    """Count syllables in a word. Uses syllabreak if available, else heuristic."""
    if _init_syllable_counter():
        try:
            result = _SYLLABLE_COUNTER.count(word, lang=lang)
            return max(result, 1)
        except Exception:
            pass
    return _count_syllables_heuristic(word, lang)


def _count_syllables_heuristic(word: str, lang: str = "en") -> int:
    """Heuristic syllable counting. Russian: vowel count. English: vowel groups."""
    word_lower = word.lower()
    if lang == "ru":
        vowels = "аеёиоуыэюя"
        count = sum(1 for ch in word_lower if ch in vowels)
    else:
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        for ch in word_lower:
            is_vowel = ch in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        if word_lower.endswith('e') and count > 1:
            count -= 1
    return max(count, 1)


# ─── SurfaceStyleTracker ───

class SurfaceStyleTracker:
    """Extracts surface-level linguistic features from user messages.

    Bilingual: English (en, default) and Russian (ru).
    Uses spaCy with en_core_web_sm (English) or ru_core_news_sm (Russian).
    Markers loaded from locales.py.
    Does NOT maintain EMA — feature extraction only. Accumulation is external.
    """

    ALL_CAPS = re.compile(r'\b[A-ZА-ЯЁ]{2,}\b')
    LONG_WORD = re.compile(r'\b\w{9,}\b')
    WORD = re.compile(r'\b\w+\b')

    def __init__(self, nlp: Optional[spacy.Language] = None, lang: str = "en"):
        self.lang = lang
        if nlp is not None:
            self.nlp = nlp
        else:
            self.nlp = self._load_spacy_model(lang)
        self.L = EN if lang == "en" else RU
        self._update_markers()

    @staticmethod
    def _load_spacy_model(lang: str) -> spacy.Language:
        model_map = {
            "ru": "ru_core_news_sm",
            "en": "en_core_web_sm",
        }
        model_name = model_map.get(lang, "en_core_web_sm")
        try:
            return spacy.load(model_name)
        except OSError:
            spacy.cli.download(model_name)
            return spacy.load(model_name)

    def set_language(self, lang: str) -> None:
        """Switch language and reload spaCy model + markers."""
        if lang != self.lang:
            self.lang = lang
            self.nlp = self._load_spacy_model(lang)
            self.L = EN if lang == "en" else RU
            self._update_markers()

    def _update_markers(self) -> None:
        """Load marker lists from current locale."""
        self.HEDGING_MARKERS = self.L.get("surface_hedging", [])
        self.FIGURATIVE_MARKERS = self.L.get("surface_figurative", [])
        self.EVALUATIVE_MARKERS = self.L.get("surface_evaluative", [])

    def _tokenize(self, text: str) -> list[str]:
        return self.WORD.findall(text.lower())

    def extract(self, messages: list[str]) -> dict[str, float]:
        """Extract surface-level linguistic features from a list of messages."""
        if not messages:
            return self._empty()

        msg_lengths: list[int] = []
        sentence_lengths: list[int] = []
        question_count = 0
        emphasis_count = 0

        hedging_count = 0
        figurative_count = 0
        evaluative_count = 0

        adjective_count = 0
        imperative_count = 0
        passive_count = 0
        participle_count = 0
        pronoun_subject_count = 0
        conditional_count = 0
        reflexive_count = 0
        first_person_count = 0
        declarative_count = 0

        total_tokens = 0
        total_pos_tokens = 0
        total_sentences = 0

        total_syllables = 0
        complex_word_count = 0
        total_word_count = 0

        complex_threshold = 4 if self.lang == "ru" else 3

        all_text_lower = []

        for msg in messages:
            tokens = self._tokenize(msg)
            msg_len = len(tokens)
            msg_lengths.append(msg_len)
            total_tokens += msg_len

            if "?" in msg:
                question_count += 1
            emphasis_count += msg.count("!") + len(self.ALL_CAPS.findall(msg))

            msg_lower = msg.lower()
            all_text_lower.append(msg_lower)

            for marker in self.HEDGING_MARKERS:
                hedging_count += msg_lower.count(marker)
            for marker in self.FIGURATIVE_MARKERS:
                figurative_count += msg_lower.count(marker)
            for marker in self.EVALUATIVE_MARKERS:
                evaluative_count += msg_lower.count(marker)

            doc = self.nlp(msg)

            sents = list(doc.sents)
            total_sentences += len(sents)

            for sent in sents:
                sent_tokens = [t for t in sent if not t.is_punct and not t.is_space]
                sent_len = len(sent_tokens)
                if sent_len > 0:
                    sentence_lengths.append(sent_len)

                sent_text = sent.text.strip()
                sent_lower = sent_text.lower()
                if "?" not in sent_text and not any(sent_lower.startswith(m) for m in self.HEDGING_MARKERS):
                    declarative_count += 1

            for token in doc:
                if token.is_punct or token.is_space:
                    continue
                total_pos_tokens += 1

                if token.pos_ == "ADJ":
                    adjective_count += 1

                if token.pos_ == "PRON" and token.morph.get("Person") == ["1"]:
                    first_person_count += 1

                if token.morph.get("Mood") == ["Imp"]:
                    imperative_count += 1

                if token.morph.get("Mood") == ["Cnd"]:
                    conditional_count += 1

                if token.morph.get("Reflex") == ["Yes"]:
                    reflexive_count += 1

                if token.dep_ == "nsubj:pass":
                    passive_count += 1

                if token.pos_ == "VERB" and (
                        token.morph.get("VerbForm") == ["Part"] or
                        token.morph.get("VerbForm") == ["Conv"]
                ):
                    participle_count += 1

                if token.dep_ in ("nsubj", "nsubj:pass") and token.pos_ == "PRON":
                    pronoun_subject_count += 1

                if token.is_alpha:
                    word_text = token.text.lower()
                    syl_count = _count_syllables(word_text, self.lang)
                    total_syllables += syl_count
                    total_word_count += 1
                    if syl_count >= complex_threshold:
                        complex_word_count += 1

        n_messages = len(messages)
        denom_tokens = max(total_tokens, 1)
        denom_pos = max(total_pos_tokens, 1)
        denom_sentences = max(total_sentences, 1)
        denom_words = max(total_word_count, 1)

        combined_text_lower = " ".join(all_text_lower)
        all_tokens = self._tokenize(combined_text_lower)

        avg_sent_len_val = statistics.mean(sentence_lengths) if sentence_lengths else 0.0
        complex_word_pct = (complex_word_count / denom_words) * 100
        fog_index = 0.4 * (avg_sent_len_val + complex_word_pct)

        return {
            "avg_msg_length_tokens": statistics.mean(msg_lengths) if msg_lengths else 0.0,
            "avg_sentence_length": avg_sent_len_val,
            "question_ratio": question_count / n_messages,
            "emphasis_ratio": emphasis_count / denom_tokens,
            "adjective_density": (adjective_count / denom_tokens) * 100,
            "first_person_ratio": first_person_count / denom_tokens,
            "imperative_ratio": imperative_count / denom_tokens,
            "conditional_ratio": conditional_count / denom_tokens,
            "reflexive_ratio": reflexive_count / denom_tokens,
            "passive_ratio": passive_count / denom_tokens,
            "participle_ratio": participle_count / denom_tokens,
            "pronoun_subject_ratio": pronoun_subject_count / denom_tokens,
            "declarative_ratio": declarative_count / denom_tokens,
            "hedging_ratio": hedging_count / denom_tokens,
            "evaluative_ratio": evaluative_count / denom_tokens,
            "figurative_markers_ratio": figurative_count / denom_tokens,
            "long_word_ratio": len(self.LONG_WORD.findall(combined_text_lower)) / denom_tokens,
            "unique_word_ratio": len(set(all_tokens)) / denom_tokens,
            "fog_index": fog_index,
            "complex_word_ratio": complex_word_count / denom_words,
        }

    def _empty(self) -> dict[str, float]:
        return {
            "avg_msg_length_tokens": 0.0,
            "avg_sentence_length": 0.0,
            "question_ratio": 0.0,
            "emphasis_ratio": 0.0,
            "adjective_density": 0.0,
            "first_person_ratio": 0.0,
            "imperative_ratio": 0.0,
            "conditional_ratio": 0.0,
            "reflexive_ratio": 0.0,
            "passive_ratio": 0.0,
            "participle_ratio": 0.0,
            "pronoun_subject_ratio": 0.0,
            "declarative_ratio": 0.0,
            "hedging_ratio": 0.0,
            "evaluative_ratio": 0.0,
            "figurative_markers_ratio": 0.0,
            "long_word_ratio": 0.0,
            "unique_word_ratio": 0.0,
            "fog_index": 0.0,
            "complex_word_ratio": 0.0,
        }