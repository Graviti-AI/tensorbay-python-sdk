#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Word, LabeledSentence, SentenceSubcatalog.

:class:`SentenceSubcatalog` defines the subcatalog for audio transcripted sentence type of labels.

:class:`Word` is a word within a phonetic transcription sentence,
containing the content of the word, the start and end time in the audio.

:class:`LabeledSentence` is the transcripted sentence type of label.
which is often used for tasks such as automatic speech recognition.

"""

from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar, Union

from ..utility import AttrsMixin, ReprMixin, attr, camel, common_loads
from .basic import SubcatalogBase, _LabelBase
from .supports import AttributesMixin


class SentenceSubcatalog(SubcatalogBase, AttributesMixin):
    """This class defines the subcatalog for audio transcripted sentence type of labels.

    Arguments:
        is_sample: A boolen value indicates whether time format is sample related.
        sample_rate: The number of samples of audio carried per second.
        lexicon: A list consists all of text and phone.

    Attributes:
        description: The description of the entire sentence subcatalog.
        is_sample: A boolen value indicates whether time format is sample related.
        sample_rate: The number of samples of audio carried per second.
        lexicon: A list consists all of text and phone.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.

    Raises:
        TypeError: When sample_rate is None and is_sample is True.

    Examples:
        *Initialization Method 1:* Init from ``SentenceSubcatalog.__init__()``.

        >>> SentenceSubcatalog(True, 16000, [["mean", "m", "iy", "n"]])
        SentenceSubcatalog(
          (is_sample): True,
          (sample_rate): 16000,
          (lexicon): [...]
        )

        *Initialization Method 2:* Init from ``SentenceSubcatalog.loads()`` method.

        >>> contents = {
        ...     "isSample": True,
        ...     "sampleRate": 16000,
        ...     "lexicon": [["mean", "m", "iy", "n"]],
        ...     "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ... }
        >>> SentenceSubcatalog.loads(contents)
        SentenceSubcatalog(
          (is_sample): True,
          (sample_rate): 16000,
          (attributes): NameList [...],
          (lexicon): [...]
        )

    """

    is_sample: bool = attr(key=camel, default=False)
    sample_rate: int = attr(is_dynamic=True, key=camel)
    lexicon: List[List[str]] = attr(is_dynamic=True)

    def __init__(
        self,
        is_sample: bool = False,
        sample_rate: Optional[int] = None,
        lexicon: Optional[List[List[str]]] = None,
    ) -> None:
        SubcatalogBase.__init__(self)
        if is_sample and not sample_rate:
            raise TypeError(
                f"Require 'sample_rate' to init {self.__class__.__name__} when is_sample is True"
            )

        self.is_sample = is_sample
        if sample_rate:
            self.sample_rate = sample_rate
        if lexicon:
            self.lexicon = lexicon

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of this SentenceSubcatalog into a dict.

        Returns:
            A dict containing all information of this SentenceSubcatalog.

        Examples:
            >>> sentence_subcatalog = SentenceSubcatalog(True, 16000, [["mean", "m", "iy", "n"]])
            >>> sentence_subcatalog.dumps()
            {'isSample': True, 'sampleRate': 16000, 'lexicon': [['mean', 'm', 'iy', 'n']]}

        """
        return self._dumps()

    def append_lexicon(self, lexemes: List[str]) -> None:
        """Add lexemes to lexicon.

        Arguments:
            lexemes: A list consists of text and phone.

        Examples:
            >>> sentence_subcatalog = SentenceSubcatalog(True, 16000, [["mean", "m", "iy", "n"]])
            >>> sentence_subcatalog.append_lexicon(["example"])
            >>> sentence_subcatalog.lexicon
            [['mean', 'm', 'iy', 'n'], ['example']]

        """
        if hasattr(self, "lexicon"):
            self.lexicon.append(lexemes)
        else:
            self.lexicon = [lexemes]


class Word(ReprMixin, AttrsMixin):
    """This class defines the concept of word.

    :class:`Word` is a word within a phonetic transcription sentence,
    containing the content of the word, the start and end time in the audio.

    Arguments:
        text: The content of the word.
        begin: The begin time of the word in the audio.
        end: The end time of the word in the audio.

    Attributes:
        text: The content of the word.
        begin: The begin time of the word in the audio.
        end: The end time of the word in the audio.

    Examples:
        >>> Word(text="example", begin=1, end=2)
        Word(
          (text): 'example',
          (begin): 1,
          (end): 2
        )

    """

    _T = TypeVar("_T", bound="Word")

    _repr_attrs = ("text", "begin", "end")

    text: str = attr()
    begin: float = attr(is_dynamic=True)
    end: float = attr(is_dynamic=True)

    def __init__(
        self,
        text: str,
        begin: Optional[float] = None,
        end: Optional[float] = None,
    ):
        self.text = text
        if begin is not None:
            self.begin = begin
        if end is not None:
            self.end = end

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Union[str, float]]) -> _T:
        """Loads a Word from a dict containing the information of the word.

        Arguments:
            contents: A dict containing the information of the word

        Returns:
            The loaded :class:`Word` object.

        Examples:
            >>> contents = {"text": "Hello, World", "begin": 1, "end": 2}
            >>> Word.loads(contents)
            Word(
              (text): 'Hello, World',
              (begin): 1,
              (end): 2
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Union[str, float]]:
        """Dumps the current word into a dict.

        Returns:
            A dict containing all the information of the word

        Examples:
            >>> word = Word(text="example", begin=1, end=2)
            >>> word.dumps()
            {'text': 'example', 'begin': 1, 'end': 2}

        """
        return self._dumps()


class LabeledSentence(_LabelBase):
    """This class defines the concept of phonetic transcription lable.

    :class:`LabeledSentence` is the transcripted sentence type of label.
    which is often used for tasks such as automatic speech recognition.

    Arguments:
        sentence: A list of sentence.
        spell: A list of spell, only exists in Chinese language.
        phone: A list of phone.
        attributes: The attributes of the label.

    Attributes:
        sentence: The transcripted sentence.
        spell: The spell within the sentence, only exists in Chinese language.
        phone: The phone of the sentence label.
        attributes: The attributes of the label.

    Examples:
        >>> sentence = [Word(text="qi1shi2", begin=1, end=2)]
        >>> spell = [Word(text="qi1", begin=1, end=2)]
        >>> phone = [Word(text="q", begin=1, end=2)]
        >>> LabeledSentence(
        ...     sentence,
        ...     spell,
        ...     phone,
        ...     attributes={"key": "value"},
        ... )
        LabeledSentence(
          (sentence): [
            Word(
              (text): 'qi1shi2',
              (begin): 1,
              (end): 2
            )
          ],
          (spell): [
            Word(
              (text): 'qi1',
              (begin): 1,
              (end): 2
            )
          ],
          (phone): [
            Word(
              (text): 'q',
              (begin): 1,
              (end): 2
            )
          ],
          (attributes): {
            'key': 'value'
          }
        )

    """

    _T = TypeVar("_T", bound="LabeledSentence")

    _repr_attrs = ("sentence", "spell", "phone", "attributes")
    _repr_maxlevel = 3

    sentence: List[Word] = attr(is_dynamic=True)
    spell: List[Word] = attr(is_dynamic=True)
    phone: List[Word] = attr(is_dynamic=True)

    def __init__(
        self,
        sentence: Optional[Iterable[Word]] = None,
        spell: Optional[Iterable[Word]] = None,
        phone: Optional[Iterable[Word]] = None,
        *,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(attributes=attributes)
        if sentence:
            self.sentence = list(sentence)
        if spell:
            self.spell = list(spell)
        if phone:
            self.phone = list(phone)

    @staticmethod
    def _load_word(contents: Iterable[Dict[str, Any]]) -> List[Word]:
        return [Word.loads(word) for word in contents]

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledSentence from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the sentence label.

        Returns:
            The loaded :class:`LabeledSentence` object.

        Examples:
            >>> contents = {
            ...     "sentence": [{"text": "qi1shi2", "begin": 1, "end": 2}],
            ...     "spell": [{"text": "qi1", "begin": 1, "end": 2}],
            ...     "phone": [{"text": "q", "begin": 1, "end": 2}],
            ...     "attributes": {"key": "value"},
            ... }
            >>> LabeledSentence.loads(contents)
            LabeledSentence(
              (sentence): [
                Word(
                  (text): 'qi1shi2',
                  (begin): 1,
                  (end): 2
                )
              ],
              (spell): [
                Word(
                  (text): 'qi1',
                  (begin): 1,
                  (end): 2
                )
              ],
              (phone): [
                Word(
                  (text): 'q',
                  (begin): 1,
                  (end): 2
                )
              ],
              (attributes): {
                'key': 'value'
              }
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current label into a dict.

        Returns:
            A dict containing all the information of the sentence label.

        Examples:
            >>> sentence = [Word(text="qi1shi2", begin=1, end=2)]
            >>> spell = [Word(text="qi1", begin=1, end=2)]
            >>> phone = [Word(text="q", begin=1, end=2)]
            >>> labeledsentence = LabeledSentence(
            ...     sentence,
            ...     spell,
            ...     phone,
            ...     attributes={"key": "value"},
            ... )
            >>> labeledsentence.dumps()
            {
                'attributes': {'key': 'value'},
                'sentence': [{'text': 'qi1shi2', 'begin': 1, 'end': 2}],
                'spell': [{'text': 'qi1', 'begin': 1, 'end': 2}],
                'phone': [{'text': 'q', 'begin': 1, 'end': 2}]
            }

        """
        return self._dumps()
