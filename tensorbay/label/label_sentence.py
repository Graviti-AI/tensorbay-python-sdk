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

from ..utility import ReprMixin, SubcatalogTypeRegister, TypeRegister, common_loads
from .basic import LabelType, SubcatalogBase, _LabelBase
from .supports import SupportAttributes


@SubcatalogTypeRegister(LabelType.SENTENCE)
class SentenceSubcatalog(SubcatalogBase, SupportAttributes):
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
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.

    Raises:
        TypeError: When sample_rate is None and is_sample is True.

    """

    def __init__(
        self,
        is_sample: bool = False,
        sample_rate: Optional[int] = None,
        lexicon: Optional[List[List[str]]] = None,
    ) -> None:
        if is_sample and not sample_rate:
            raise TypeError(
                f"Require 'sample_rate' to init {self.__class__.__name__} when is_sample is True"
            )

        self.is_sample = is_sample
        if sample_rate:
            self.sample_rate = sample_rate
        if lexicon:
            self.lexicon = lexicon

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        self.is_sample = contents.get("isSample", False)

        if self.is_sample:
            self.sample_rate = contents["sampleRate"]

        lexicon = contents.get("lexicon")
        if lexicon:
            self.lexicon = lexicon
        if "lexicon" in contents:
            self.lexicon = contents["lexicon"]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of this SentenceSubcatalog into a dict.

        Returns:
            A dict containing all information of this SentenceSubcatalog.

        """
        contents = super().dumps()

        if self.is_sample:
            contents["isSample"] = self.is_sample
            contents["sampleRate"] = self.sample_rate

        if hasattr(self, "lexicon"):
            contents["lexicon"] = self.lexicon

        return contents

    def append_lexicon(self, lexemes: List[str]) -> None:
        """Add lexemes to lexicon.

        Arguments:
            lexemes: A list consists of text and phone.

        """
        if hasattr(self, "lexicon"):
            self.lexicon.append(lexemes)
        else:
            self.lexicon = [lexemes]


class Word(ReprMixin):
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

    """

    _T = TypeVar("_T", bound="Word")

    _repr_attrs = ("text", "begin", "end")

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

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.text = contents["text"]

        if "begin" in contents:
            self.begin = contents["begin"]

        if "end" in contents:
            self.end = contents["end"]

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Union[str, float]]) -> _T:
        """Loads a Word from a dict containing the information of the word.

        Arguments:
            contents: A dict containing the information of the word,
                whose format should be like::

                    {
                        "text": str ,
                        "begin": float,
                        "end": float,
                    }

        Returns:
            The loaded :class:`Word` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Union[str, float]]:
        """Dumps the current word into a dict.

        Returns:
            A dict containing all the information of the word,
            whose format is like::

                {
                    "text": str ,
                    "begin": float,
                    "end": float,
                }

        """
        contents: Dict[str, Union[str, float]] = {"text": self.text}
        if hasattr(self, "begin"):
            contents["begin"] = self.begin
        if hasattr(self, "end"):
            contents["end"] = self.end
        return contents


@TypeRegister(LabelType.SENTENCE)  # pylint: disable=too-few-public-methods
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

    """

    _T = TypeVar("_T", bound="LabeledSentence")

    _label_attrs = ("attributes",)

    _repr_attrs = ("sentence", "spell", "phone") + _label_attrs
    _repr_maxlevel = 3

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

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)

        if "sentence" in contents:
            self.sentence = self._load_word(contents["sentence"])

        if "spell" in contents:
            self.spell = self._load_word(contents["spell"])

        if "phone" in contents:
            self.phone = self._load_word(contents["phone"])

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledSentence from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the sentence label,
                whose format should be like::

                    {
                        "sentence": [
                            {
                                "text":  <str>
                                "begin": <float>
                                "end":   <float>
                            }
                            ...
                            ...
                        ],
                        "spell": [
                            {
                                "text":  <str>
                                "begin": <float>
                                "end":   <float>
                            }
                            ...
                            ...
                        ],
                        "phone": [
                            {
                                "text":  <str>
                                "begin": <float>
                                "end":   <float>
                            }
                            ...
                            ...
                        ],
                        "attributes": {
                            <key>: <value>,
                            ...
                            ...
                        }
                    }

        Returns:
            The loaded :class:`LabeledSentence` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current label into a dict.

        Returns:
            A dict containing all the information of the sentence label,
            whose format is like::

                {
                    "sentence": [
                        {
                            "text":  <str>
                            "begin": <float>
                            "end":   <float>
                        }
                        ...
                        ...
                    ],
                    "spell": [
                        {
                            "text":  <str>
                            "begin": <float>
                            "end":   <float>
                        }
                        ...
                        ...
                    ],
                    "phone": [
                        {
                            "text":  <str>
                            "begin": <float>
                            "end":   <float>
                        }
                        ...
                        ...
                    ],
                    "attributes": {
                        <key>: <value>,
                        ...
                        ...
                    }
                }

        """
        contents = _LabelBase.dumps(self)
        if hasattr(self, "sentence"):
            contents["sentence"] = [word.dumps() for word in self.sentence]
        if hasattr(self, "spell"):
            contents["spell"] = [word.dumps() for word in self.spell]
        if hasattr(self, "phone"):
            contents["phone"] = [word.dumps() for word in self.phone]
        return contents
