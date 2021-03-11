#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import LabeledSentence, SentenceSubcatalog, Word
from ..supports import SupportAttributes

_ATTRIBUTES = {"key": "value"}
_ENUMS = ["male", "female"]

_TEXT = "Hello, World"
_BEGIN = 1
_END = 1

_WORD_DATA = {"text": "Hello, World", "begin": 1, "end": 1}

_LABELEDSENTENCE_DATA = {
    "sentence": [{"text": "qi1shi2", "begin": 1, "end": 1}],
    "spell": [{"text": "qi1", "begin": 1, "end": 1}],
    "phone": [{"text": "q", "begin": 1, "end": 1}],
    "attributes": {"key": "value"},
}
_LEXICON = ["mean", "m", "iy", "n"]
_SENTENCE_SUBCATALOG = {
    "isSample": True,
    "sampleRate": 16000,
    "lexicon": [_LEXICON],
    "attributes": [{"name": "gender", "enum": _ENUMS}],
}


class TestWord:
    def test_init(self):
        word = Word(text=_TEXT, begin=_BEGIN, end=_END)

        assert word.text == _TEXT
        assert word.begin == _BEGIN
        assert word.end == _END

    def test_eq(self):
        word1 = Word("Hello", 0, 1)
        word2 = Word("Hello", 0, 1)
        word3 = Word("Hello World", 0, 2)

        assert word1 == word2
        assert word1 != word3

    def test_loads(self):
        word = Word.loads(_WORD_DATA)

        assert word.text == _TEXT
        assert word.begin == _BEGIN
        assert word.end == _END

    def test_dumps(self):
        word = Word(text=_TEXT, begin=_BEGIN, end=_END)

        assert word.dumps() == _WORD_DATA


class TestLabeledSentence:
    def test_init(self):
        sentence = [Word(text="qi1shi2", begin=_BEGIN, end=_END)]
        spell = [Word(text="qi1", begin=_BEGIN, end=_END)]
        phone = [Word(text="q", begin=_BEGIN, end=_END)]

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes=_ATTRIBUTES
        )

        assert labeledsentence.sentence == list(sentence)
        assert labeledsentence.spell == list(spell)
        assert labeledsentence.phone == list(phone)

    def test_eq(self):
        sentence1 = LabeledSentence([Word("Hello", 0, 1)])
        sentence2 = LabeledSentence([Word("Hello", 0, 1)])
        sentence3 = LabeledSentence([Word("Hello World", 0, 2)])

        assert sentence1 == sentence2
        assert sentence1 != sentence3

    def test_load_word(self):
        sentence = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["sentence"])
        spell = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["spell"])
        phone = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["phone"])

        assert sentence[0].text == "qi1shi2"
        assert sentence[0].begin == _BEGIN
        assert sentence[0].end == _END

        assert spell[0].text == "qi1"
        assert spell[0].begin == _BEGIN
        assert spell[0].end == _END

        assert phone[0].text == "q"
        assert phone[0].begin == _BEGIN
        assert phone[0].end == _END

    def test_loads(self):
        labeledsentence = LabeledSentence.loads(_LABELEDSENTENCE_DATA)

        assert labeledsentence.sentence[0].text == _LABELEDSENTENCE_DATA["sentence"][0]["text"]
        assert labeledsentence.sentence[0].begin == _LABELEDSENTENCE_DATA["sentence"][0]["begin"]
        assert labeledsentence.sentence[0].end == _LABELEDSENTENCE_DATA["sentence"][0]["end"]

        assert labeledsentence.spell[0].text == _LABELEDSENTENCE_DATA["spell"][0]["text"]
        assert labeledsentence.spell[0].begin == _LABELEDSENTENCE_DATA["spell"][0]["begin"]
        assert labeledsentence.spell[0].end == _LABELEDSENTENCE_DATA["spell"][0]["end"]

        assert labeledsentence.phone[0].text == _LABELEDSENTENCE_DATA["phone"][0]["text"]
        assert labeledsentence.phone[0].begin == _LABELEDSENTENCE_DATA["phone"][0]["begin"]
        assert labeledsentence.phone[0].end == _LABELEDSENTENCE_DATA["phone"][0]["end"]

    def test_dumps(self):
        sentence = [Word(text="qi1shi2", begin=_BEGIN, end=_END)]
        spell = [Word(text="qi1", begin=_BEGIN, end=_END)]
        phone = [Word(text="q", begin=_BEGIN, end=_END)]

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes=_ATTRIBUTES
        )

        labeledsentence.dumps = _LABELEDSENTENCE_DATA


class TestSentenceSubcatalog:
    def test_init_subclass(self):
        sentence_subcatalog = SentenceSubcatalog()
        assert sentence_subcatalog._supports == (SupportAttributes,)

    def test_init(self):
        with pytest.raises(TypeError):
            SentenceSubcatalog(True)
        sentence_subcatalog = SentenceSubcatalog(True, 16000, [_LEXICON])
        assert sentence_subcatalog.is_sample == True
        assert sentence_subcatalog.sample_rate == 16000
        assert sentence_subcatalog.lexicon == [_LEXICON]

    def test_eq(self):
        content1 = {
            "isSample": True,
            "sampleRate": 16000,
            "lexicon": ["mean", "m", "iy", "n"],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        content2 = {
            "isSample": True,
            "sampleRate": 16000,
            "lexicon": ["mean", "m"],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        sentence_subcatalog1 = SentenceSubcatalog.loads(content1)
        sentence_subcatalog2 = SentenceSubcatalog.loads(content1)
        sentence_subcatalog3 = SentenceSubcatalog.loads(content2)

        assert sentence_subcatalog1 == sentence_subcatalog2
        assert sentence_subcatalog1 != sentence_subcatalog3

    def test_loads(self, attributes):
        sentence_subcatalog = SentenceSubcatalog.loads(_SENTENCE_SUBCATALOG)
        assert sentence_subcatalog.is_sample == _SENTENCE_SUBCATALOG["isSample"]
        assert sentence_subcatalog.sample_rate == _SENTENCE_SUBCATALOG["sampleRate"]
        assert sentence_subcatalog.lexicon == _SENTENCE_SUBCATALOG["lexicon"]
        assert sentence_subcatalog.attributes == attributes

    def test_dumps(self, attributes):
        sentence_subcatalog = SentenceSubcatalog(
            _SENTENCE_SUBCATALOG["isSample"],
            _SENTENCE_SUBCATALOG["sampleRate"],
            _SENTENCE_SUBCATALOG["lexicon"],
        )
        sentence_subcatalog.attributes = attributes
        assert sentence_subcatalog.dumps() == _SENTENCE_SUBCATALOG

    def append_lexicon(self):
        sentence_subcatalog = SentenceSubcatalog()
        sentence_subcatalog.append_lexicon(_LEXICON)
        assert sentence_subcatalog.lexicon == [_LEXICON]
