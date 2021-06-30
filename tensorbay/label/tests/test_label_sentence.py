#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import LabeledSentence, SentenceSubcatalog, Word

_LEXICON = ["mean", "m", "iy", "n"]


@pytest.fixture
def subcatalog_sentence(attributes_catalog_data):
    return {
        "isSample": True,
        "sampleRate": 16000,
        "lexicon": [_LEXICON],
        "attributes": attributes_catalog_data,
    }


class TestWord:
    def test_init(self):
        word = Word(text="Hello", begin=1, end=3)

        assert word.text == "Hello"
        assert word.begin == 1
        assert word.end == 3

    def test_eq(self):
        word1 = Word("Hello", 0, 1)
        word2 = Word("Hello", 0, 1)
        word3 = Word("Hello World", 0, 2)

        assert word1 == word2
        assert word1 != word3

    def test_loads(self):
        word = Word.loads({"text": "Hello", "begin": 1, "end": 3})

        assert word.text == "Hello"
        assert word.begin == 1
        assert word.end == 3

    def test_dumps(self):
        word = Word(text="Hello", begin=1, end=3)

        assert word.dumps() == {"text": "Hello", "begin": 1, "end": 3}


class TestLabeledSentence:
    def test_init(self):
        sentence = [Word(text="qi1shi2", begin=1, end=3)]
        spell = [Word(text="qi1", begin=1, end=3)]
        phone = [Word(text="q", begin=1, end=3)]

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes={"gender": "male"}
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
        sentence = LabeledSentence._load_word([{"text": "qi1shi2", "begin": 1, "end": 3}])
        spell = LabeledSentence._load_word([{"text": "qi1", "begin": 1, "end": 2}])
        phone = LabeledSentence._load_word([{"text": "q", "begin": 1, "end": 1.5}])

        assert sentence[0].text == "qi1shi2"
        assert sentence[0].begin == 1
        assert sentence[0].end == 3

        assert spell[0].text == "qi1"
        assert spell[0].begin == 1
        assert spell[0].end == 2

        assert phone[0].text == "q"
        assert phone[0].begin == 1
        assert phone[0].end == 1.5

    def test_loads(self):
        contents = {
            "sentence": [{"text": "qi1shi2", "begin": 1, "end": 3}],
            "spell": [{"text": "qi1", "begin": 1, "end": 2}],
            "phone": [{"text": "q", "begin": 1, "end": 1.5}],
            "attributes": {"gender": "male"},
        }
        labeledsentence = LabeledSentence.loads(contents)

        assert labeledsentence.sentence[0].text == "qi1shi2"
        assert labeledsentence.sentence[0].begin == 1
        assert labeledsentence.sentence[0].end == 3

        assert labeledsentence.spell[0].text == "qi1"
        assert labeledsentence.spell[0].begin == 1
        assert labeledsentence.spell[0].end == 2

        assert labeledsentence.phone[0].text == "q"
        assert labeledsentence.phone[0].begin == 1
        assert labeledsentence.phone[0].end == 1.5

    def test_dumps(self):
        sentence = [Word(text="qi1shi2", begin=1, end=3)]
        spell = [Word(text="qi1", begin=1, end=2)]
        phone = [Word(text="q", begin=1, end=1.5)]

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes={"gender": "male"}
        )

        labeledsentence.dumps = {
            "sentence": [{"text": "qi1shi2", "begin": 1, "end": 3}],
            "spell": [{"text": "qi1", "begin": 1, "end": 2}],
            "phone": [{"text": "q", "begin": 1, "end": 1.5}],
            "attributes": {"gender": "male"},
        }


class TestSentenceSubcatalog:
    def test_init(self):
        with pytest.raises(TypeError):
            SentenceSubcatalog(True)
        sentence_subcatalog = SentenceSubcatalog(True, 16000, [_LEXICON])
        assert sentence_subcatalog.is_sample == True
        assert sentence_subcatalog.sample_rate == 16000
        assert sentence_subcatalog.lexicon == [_LEXICON]

    def test_eq(self):
        contents1 = {
            "isSample": True,
            "sampleRate": 16000,
            "lexicon": ["mean", "m", "iy", "n"],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        contents2 = {
            "isSample": True,
            "sampleRate": 16000,
            "lexicon": ["mean", "m"],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        sentence_subcatalog1 = SentenceSubcatalog.loads(contents1)
        sentence_subcatalog2 = SentenceSubcatalog.loads(contents1)
        sentence_subcatalog3 = SentenceSubcatalog.loads(contents2)

        assert sentence_subcatalog1 == sentence_subcatalog2
        assert sentence_subcatalog1 != sentence_subcatalog3

    def test_loads(self, attributes, subcatalog_sentence):
        sentence_subcatalog = SentenceSubcatalog.loads(subcatalog_sentence)
        assert sentence_subcatalog.is_sample == subcatalog_sentence["isSample"]
        assert sentence_subcatalog.sample_rate == subcatalog_sentence["sampleRate"]
        assert sentence_subcatalog.lexicon == subcatalog_sentence["lexicon"]
        assert sentence_subcatalog.attributes == attributes

    def test_dumps(self, attributes, subcatalog_sentence):
        sentence_subcatalog = SentenceSubcatalog(
            subcatalog_sentence["isSample"],
            subcatalog_sentence["sampleRate"],
            subcatalog_sentence["lexicon"],
        )
        sentence_subcatalog.attributes = attributes
        assert sentence_subcatalog.dumps() == subcatalog_sentence

    def append_lexicon(self):
        sentence_subcatalog = SentenceSubcatalog()
        sentence_subcatalog.append_lexicon(_LEXICON)
        assert sentence_subcatalog.lexicon == [_LEXICON]
