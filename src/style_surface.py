# src/style_surface.py
"""Stream B: Surface Style Features.
Bilingual: English (en, default) and Russian (ru).
Uses spaCy + pymorphy3 for Russian syllable counting and Gunning Fog Index.
"""

import re
import statistics
from typing import Optional
import spacy
import pymorphy3

# Счётчик слогов через pymorphy3 (кешируется)
_morph = None


def _get_morph():
    global _morph
    if _morph is None:
        _morph = pymorphy3.MorphAnalyzer()
    return _morph


def _count_syllables_ru(word: str) -> int:
    """Подсчёт слогов в русском слове по количеству гласных."""
    vowels = "аеёиоуыэюя"
    word_lower = word.lower()
    count = sum(1 for ch in word_lower if ch in vowels)
    return max(count, 1)


def _count_syllables_en(word: str) -> int:
    """Подсчёт слогов в английском слове.

    Эвристика: считаем группы гласных как один слог.
    Работает в ~90% случаев, для точного подсчёта нужен словарь.
    """
    word_lower = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for ch in word_lower:
        is_vowel = ch in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    # Немые 'e' в конце
    if word_lower.endswith('e') and count > 1:
        count -= 1
    return max(count, 1)


class SurfaceStyleTracker:
    """Extracts surface-level linguistic features from user messages.

    Bilingual: English (en, default) and Russian (ru).
    Uses spaCy with en_core_web_sm (English) or ru_core_news_sm (Russian).
    Does NOT maintain EMA — feature extraction only. Accumulation is external.
    """

    # Маркеры: русские
    HEDGING_MARKERS_RU = [
        "вероятно", "возможно", "кажется", "по-видимому", "видимо",
        "скорее всего", "вроде", "вроде бы", "как бы", "типа",
        "похоже", "предположительно", "допустим", "может быть",
        "не исключено", "судя по всему", "я думаю", "полагаю",
        "на мой взгляд", "имхо", "по моему мнению",
    ]

    FIGURATIVE_MARKERS_RU = [
        "как", "словно", "будто", "точно", "подобно",
        "это как", "похоже на", "представь", "вообрази",
        "метафора", "аналогия", "сравнение", "образно",
    ]

    EVALUATIVE_MARKERS_RU = [
        "круто", "отлично", "прекрасно", "замечательно", "великолепно",
        "гениально", "потрясающе", "восхитительно", "шикарно", "класс",
        "здорово", "чудесно", "великий", "превосходно", "блестяще",
        "обалденно", "кайф", "огонь", "топ", "имба",
        "ужасно", "отвратительно", "мерзко", "чудовищно", "гадко",
        "противно", "бесит", "раздражает", "тупо", "глупо",
        "идиотский", "дурацкий", "никуда", "провал", "катастрофа",
        "позор", "бред", "чушь", "ерунда", "фигня",
        "ого", "вау", "ничего себе", "с ума сойти", "невероятно",
        "поразительно", "удивительно", "фантастика", "обалдеть",
        "какой", "какая", "какое", "какие", "насколько", "столько",
        "это же", "ведь", "просто", "вообще",
    ]

    # Маркеры: английские
    HEDGING_MARKERS_EN = [
        "probably", "possibly", "maybe", "perhaps", "apparently",
        "seemingly", "most likely", "kind of", "sort of", "i think",
        "i guess", "i suppose", "i believe", "in my opinion",
        "it seems", "it appears", "arguably", "presumably",
        "somewhat", "rather", "quite", "a bit", "a little",
        "not exactly", "not entirely", "to some extent",
    ]

    FIGURATIVE_MARKERS_EN = [
        "like", "as if", "as though", "imagine", "picture this",
        "metaphor", "analogy", "comparison", "figuratively",
        "it's like", "similar to", "think of it as",
    ]

    EVALUATIVE_MARKERS_EN = [
        "awesome", "excellent", "amazing", "wonderful", "brilliant",
        "fantastic", "incredible", "outstanding", "superb", "great",
        "terrible", "awful", "horrible", "dreadful", "disgusting",
        "nasty", "stupid", "ridiculous", "absurd", "crazy",
        "wow", "oh my god", "no way", "unbelievable",
        "remarkable", "extraordinary", "phenomenal", "stunning",
        "so", "such", "very", "really", "extremely",
    ]

    ALL_CAPS = re.compile(r'\b[A-ZА-ЯЁ]{2,}\b')
    LONG_WORD = re.compile(r'\b\w{9,}\b')
    WORD = re.compile(r'\b\w+\b')

    def __init__(self, nlp: Optional[spacy.Language] = None, lang: str = "en"):
        self.lang = lang
        if nlp is not None:
            self.nlp = nlp
        else:
            self.nlp = self._load_spacy_model(lang)
        self._morph = _get_morph()
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
            self._morph = _get_morph()
            self._update_markers()

    def _update_markers(self) -> None:
        """Set marker lists based on current language."""
        if self.lang == "ru":
            self.HEDGING_MARKERS = self.HEDGING_MARKERS_RU
            self.FIGURATIVE_MARKERS = self.FIGURATIVE_MARKERS_RU
            self.EVALUATIVE_MARKERS = self.EVALUATIVE_MARKERS_RU
        else:
            self.HEDGING_MARKERS = self.HEDGING_MARKERS_EN
            self.FIGURATIVE_MARKERS = self.FIGURATIVE_MARKERS_EN
            self.EVALUATIVE_MARKERS = self.EVALUATIVE_MARKERS_EN

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

        # Индекс Ганнинга
        total_syllables = 0
        complex_word_count = 0
        total_word_count = 0

        # Порог сложного слова: 4+ слогов для русского, 3+ для английского
        complex_threshold = 4 if self.lang == "ru" else 3
        # Выбор функции подсчёта слогов
        syllable_counter = _count_syllables_ru if self.lang == "ru" else _count_syllables_en

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

                # Индекс Ганнинга
                if token.is_alpha:
                    word_text = token.text.lower()
                    syl_count = syllable_counter(word_text)
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

        # Индекс туманности Ганнинга
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