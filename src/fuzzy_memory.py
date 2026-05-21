# src/fuzzy_memory.py
"""Stream A: Semantic cloud + keyword memory for context-aware prompts."""

import json
import logging
from pathlib import Path
from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy

logger = logging.getLogger(__name__)


class SemanticCloud:
    """Builds and maintains a semantic cloud (EMA of embeddings) from user dialogs.

    Uses E5-large with 512 token context window. Chunking only applied when
    message exceeds model limit.
    spaCy model is passed from outside (shared with other components).
    """

    MODEL_MAX_LENGTH = 512
    OVERLAP_RATIO = 0.25
    SERIALIZATION_VERSION = 1

    # Слова-паразиты (русские)
    RESPONSE_PARASITES_RU = [
        "отличный вопрос", "хороший вопрос", "интересный вопрос", "правильный вопрос",
        "отличная наблюдательность", "блестящее замечание", "точное наблюдение",
        "вы абсолютно правы", "вы совершенно правы", "вы правы", "ты абсолютно прав",
        "ты прав", "ты точно выделил", "ты верно подметил",
        "давайте разберёмся", "давайте разберемся", "давайте посмотрим",
        "вот что известно", "вот основные", "вот ключевые", "вот что важно",
        "таким образом", "итак", "короткий ответ", "краткий ответ", "прямой ответ",
        "я понимаю", "я вас понимаю", "понимаю вас", "понимаю твою",
        "я чувствую", "это очень тяжело", "это нормально",
        "спасибо за вопрос", "благодарю за вопрос",
        "надеюсь", "если захочешь", "если хотите", "если надумаешь",
        "если будут вопросы", "обращайтесь", "спрашивай",
        "резонно", "вопрос в яблочко", "верно подмечено", "ключевая брешь",
    ]

    # Слова-паразиты (английские)
    RESPONSE_PARASITES_EN = [
        "great question", "good question", "interesting question", "excellent question",
        "that's a great point", "brilliant observation", "spot on",
        "you're absolutely right", "you're right", "you're totally right",
        "you nailed it", "you got it", "exactly right",
        "let's break this down", "let's dive in", "let's explore",
        "here's what we know", "here are the key", "here's what matters",
        "in summary", "so", "the bottom line", "the short answer", "simply put",
        "i understand", "i hear you", "i see where you're coming from",
        "i feel", "that sounds really tough", "that's totally normal",
        "thanks for asking", "thank you for the question",
        "i hope", "if you'd like", "if you want", "if you're interested",
        "if you have more questions", "feel free to ask", "just ask",
        "fair point", "right on the money", "well noted", "key gap",
    ]

    def __init__(
            self,
            model_path: Optional[str] = None,
            model: Optional[SentenceTransformer] = None,
            nlp: Optional[spacy.Language] = None,
            learning_rate: float = 0.3,
            lang: str = "en",
    ):
        if model is not None:
            self.encoder = model
        elif model_path is not None:
            self.encoder = SentenceTransformer(model_path)
        else:
            raise ValueError("Either model_path or model must be provided")

        self._nlp = nlp
        self._learning_rate = learning_rate
        self.semantic_cloud: Optional[np.ndarray] = None
        self._kw_model = None
        self._stop_words: Optional[list[str]] = None
        self.lang = lang

    def set_language(self, lang: str) -> None:
        """Switch parasites language. Invalidates stop-words cache."""
        self.lang = lang
        self._stop_words = None  # принудительная перестройка кеша

    def _build_stop_words(self) -> list[str]:
        """Build and cache stop words list. Called once per language."""
        stop_words = []
        parasites = self.RESPONSE_PARASITES_RU if self.lang == "ru" else self.RESPONSE_PARASITES_EN
        for phrase in parasites:
            stop_words.extend(phrase.split())
        if self._nlp is not None:
            stop_words.extend(list(self._nlp.Defaults.stop_words))
        return list(set(stop_words))

    @property
    def _chunk_overlap(self) -> int:
        return int(self.MODEL_MAX_LENGTH * self.OVERLAP_RATIO)

    def _tokenize(self, text: str) -> list[int]:
        if not hasattr(self.encoder, 'tokenizer') or self.encoder.tokenizer is None:
            raise RuntimeError("SentenceTransformer tokenizer not available.")
        return self.encoder.tokenizer.encode(text, add_special_tokens=False)

    def _chunk_text(self, text: str) -> list[str]:
        tokens = self._tokenize(text)
        if len(tokens) <= self.MODEL_MAX_LENGTH:
            return [text]

        chunks = []
        start = 0
        while start < len(tokens):
            end = start + self.MODEL_MAX_LENGTH
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            chunks.append(chunk_text)
            start += self.MODEL_MAX_LENGTH - self._chunk_overlap

        return chunks

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        if not text or not text.strip():
            return None

        chunks = self._chunk_text(text)
        embeddings = [self.encoder.encode(f"passage: {chunk}") for chunk in chunks]

        if len(chunks) == 1:
            return embeddings[0]
        return np.mean(embeddings, axis=0)

    def process_message(self, text: str) -> None:
        emb = self.get_embedding(text)
        if emb is None:
            return

        chunks = self._chunk_text(text)
        if len(chunks) > 1:
            weight = 1.0  # чанкированное сообщение — полный вес
        else:
            token_count = len(self._tokenize(text))
            weight = min(token_count / self.MODEL_MAX_LENGTH, 1.0)

        if self.semantic_cloud is None:
            self.semantic_cloud = emb.copy()
        else:
            alpha = self._learning_rate * weight
            self.semantic_cloud = alpha * emb + (1 - alpha) * self.semantic_cloud

    def _dynamic_top_n(self, text: str, min_n: int = 1, max_n: int = 3, ratio: float = 0.1) -> int:
        word_count = len(text.split())
        calculated = int(word_count * ratio)
        return max(min_n, min(max_n, calculated))

    def _build_stop_words(self) -> list[str]:
        """Build and cache stop words list. Called once."""
        stop_words = []
        for phrase in self.RESPONSE_PARASITES:
            stop_words.extend(phrase.split())
        if self._nlp is not None:
            stop_words.extend(list(self._nlp.Defaults.stop_words))
        return list(set(stop_words))

    def _get_stop_words(self) -> list[str]:
        """Return cached stop words, building them on first call."""
        if self._stop_words is None:
            self._stop_words = self._build_stop_words()
        return self._stop_words

    def _get_raw_keywords(self, text: str, top_n: int) -> list[tuple[str, float]]:
        """Get raw KeyBERT candidates."""
        if self._kw_model is None:
            try:
                from keybert import KeyBERT
                self._kw_model = KeyBERT(model=self.encoder)
            except ImportError:
                logger.warning("KeyBERT not installed. Install with: pip install keybert")
                return []

        if not text or not text.strip():
            return []

        stop_words = self._get_stop_words()

        try:
            keywords = self._kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),
                stop_words=stop_words,
                top_n=top_n,
                use_mmr=True,
                diversity=0.5
            )
            return keywords
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return []

    def _has_noun(self, phrase: str, doc: spacy.tokens.Doc) -> bool:
        """Check if phrase contains at least one noun.

        Optimised: build noun set once, check against it.
        """
        if not hasattr(self, '_noun_cache') or self._noun_cache.get('doc') is not doc:
            noun_set = {token.text.lower() for token in doc if token.pos_ == "NOUN"}
            self._noun_cache = {'doc': doc, 'nouns': noun_set}
        else:
            noun_set = self._noun_cache['nouns']

        phrase_lower = phrase.lower()
        return any(noun in phrase_lower for noun in noun_set)

    def _has_meaningful_words(self, phrase: str, doc: spacy.tokens.Doc) -> bool:
        """Check that not ALL words are stop words or parasites."""
        if self._nlp is None:
            return True
        stop_words = set(self._get_stop_words())
        phrase_tokens = phrase.lower().split()
        meaningful = [w for w in phrase_tokens if w not in stop_words]
        return len(meaningful) > 0

    def _filter_candidates(self, candidates: list[tuple[str, float]],
                           doc: Optional[spacy.tokens.Doc]) -> list[tuple[str, float]]:
        """Filter KeyBERT candidates: must contain a noun and not be all stop words."""
        if doc is None:
            return candidates

        filtered = []
        for phrase, score in candidates:
            if self._has_meaningful_words(phrase, doc) and self._has_noun(phrase, doc):
                filtered.append((phrase, score))
        return filtered

    def _deduplicate_keywords(self, candidates: list[tuple[str, float]]) -> list[tuple[str, float]]:
        """Remove overlapping keywords. Keep longer/more specific ones."""
        if not candidates:
            return []

        candidates.sort(key=lambda x: x[1], reverse=True)

        result: list[tuple[str, float]] = []
        for phrase, score in candidates:
            phrase_lower = phrase.lower()
            replaced_existing = False

            # Проверяем, не входит ли phrase в уже отобранные
            is_substring_of_existing = False
            for selected_phrase, _ in result:
                if phrase_lower in selected_phrase.lower():
                    is_substring_of_existing = True
                    break

            if is_substring_of_existing:
                continue

            # Проверяем, не поглощает ли phrase какой-то из уже отобранных
            for i, (selected_phrase, _) in enumerate(result):
                if selected_phrase.lower() in phrase_lower:
                    result[i] = (phrase, score)
                    replaced_existing = True
                    break

            if not replaced_existing:
                result.append((phrase, score))

        return result

    def extract_keywords(self, text: str, top_n: Optional[int] = None) -> list[tuple[str, float]]:
        """Extract key phrases from text using KeyBERT + spaCy filtering.

        Args:
            text: Input text.
            top_n: Number of keywords. If None, calculated dynamically based on text length.

        Returns:
            List of (keyword, score) tuples. Empty list on failure.
        """
        if top_n is None:
            top_n = self._dynamic_top_n(text)

        if not text or not text.strip():
            return []

        raw_candidates = self._get_raw_keywords(text, max(top_n * 3, 5))

        if not raw_candidates:
            return []

        doc = self._nlp(text) if self._nlp else None
        filtered = self._filter_candidates(raw_candidates, doc)

        if not filtered:
            filtered = raw_candidates

        deduped = self._deduplicate_keywords(filtered)

        return deduped[:top_n]

    def to_dict(self) -> dict:
        return {
            "version": self.SERIALIZATION_VERSION,
            "cloud": self.semantic_cloud.tolist() if self.semantic_cloud is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict, model_path: Optional[str] = None,
                  model: Optional[SentenceTransformer] = None,
                  nlp: Optional[spacy.Language] = None) -> "SemanticCloud":
        version = data.get("version", 0)
        if version != cls.SERIALIZATION_VERSION:
            raise ValueError(f"Unsupported version {version}. Expected {cls.SERIALIZATION_VERSION}.")

        instance = cls(model_path=model_path, model=model, nlp=nlp)
        cloud = data.get("cloud")
        if cloud is not None:
            instance.semantic_cloud = np.array(cloud)
        return instance


class KeywordMemory:
    """Fuzzy associative memory: maps query keywords to response keywords."""

    MAX_KEYS = 500
    SIMILARITY_THRESHOLD = 0.6
    MIN_KEYWORD_WORDS = 2

    def __init__(self, semantic_cloud: SemanticCloud):
        self.semantic_cloud = semantic_cloud
        self.memory: dict[str, list[list[str]]] = {}
        self._access_order: list[str] = []

    def add_pair(self, user_message: str, assistant_message: str) -> None:
        """Extract keywords from a query-response pair and add to memory."""
        kw_query_list = self.semantic_cloud.extract_keywords(user_message, top_n=1)
        if not kw_query_list or not kw_query_list[0][0]:
            return
        kw_query = kw_query_list[0][0].lower().strip()

        # Извлекаем первое осмысленное предложение из ответа
        if '.' in assistant_message:
            first_sentence = assistant_message.split('.')[0]
        elif '\n' in assistant_message:
            first_sentence = assistant_message.split('\n')[0]
        else:
            first_sentence = assistant_message[:200]

        top_n = self.semantic_cloud._dynamic_top_n(first_sentence)
        kw_response_list = self.semantic_cloud.extract_keywords(first_sentence, top_n=top_n)

        kw_responses = [
            kw[0].lower().strip()
            for kw in kw_response_list
            if kw[0] and len(kw[0].split()) >= self.MIN_KEYWORD_WORDS
        ]

        if not kw_responses:
            return

        if kw_query not in self.memory:
            self.memory[kw_query] = []
        self.memory[kw_query].append(kw_responses)

        # LRU: перемещаем в конец
        if kw_query in self._access_order:
            self._access_order.remove(kw_query)
        self._access_order.append(kw_query)

        # Эвикция старых ключей
        while len(self.memory) > self.MAX_KEYS:
            oldest = self._access_order.pop(0)
            del self.memory[oldest]
            logger.debug(f"Memory evicted: {oldest}")

    def query(self, current_question: str, top_k: int = 3) -> list[str]:
        """Retrieve relevant keywords from memory for a new question."""
        if not self.memory:
            return []

        kw_current_list = self.semantic_cloud.extract_keywords(current_question, top_n=1)
        if not kw_current_list or not kw_current_list[0][0]:
            return []
        kw_current = kw_current_list[0][0].lower().strip()

        current_emb = self.semantic_cloud.get_embedding(kw_current)
        if current_emb is None:
            return []

        similarities: list[tuple[str, float]] = []
        for kw_query in self.memory:
            kw_emb = self.semantic_cloud.get_embedding(kw_query)
            if kw_emb is not None:
                sim = float(np.dot(current_emb, kw_emb))
                if sim > self.SIMILARITY_THRESHOLD:
                    similarities.append((kw_query, sim))

        if not similarities:
            return []

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_matches = similarities[:top_k]

        all_keywords = []
        seen = set()
        for kw_query, _ in top_matches:
            for response_kws in self.memory[kw_query]:
                for kw in response_kws:
                    kw_lower = kw.lower().strip()
                    if kw_lower not in seen:
                        all_keywords.append(kw)
                        seen.add(kw_lower)

        # LRU: обновляем порядок для использованных ключей
        for kw_query, _ in top_matches:
            if kw_query in self._access_order:
                self._access_order.remove(kw_query)
                self._access_order.append(kw_query)

        logger.debug(f"Memory query '{kw_current}' matched: {[m[0] for m in top_matches]}")
        return all_keywords

    def to_dict(self) -> dict:
        return {
            "memory": self.memory,
            "access_order": self._access_order,
        }

    @classmethod
    def from_dict(cls, data: dict, semantic_cloud: SemanticCloud) -> "KeywordMemory":
        instance = cls(semantic_cloud)
        instance.memory = data.get("memory", {})
        instance._access_order = data.get("access_order", [])
        return instance