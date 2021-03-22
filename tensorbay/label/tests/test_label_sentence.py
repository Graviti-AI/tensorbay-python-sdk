#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from .. import LabeledSentence, Word

_ATTRIBUTES = {"key": "value"}

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
