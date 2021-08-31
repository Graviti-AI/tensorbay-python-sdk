**********
 Sentence
**********

Sentence label is the transcripted sentence of a piece of audio,
which is often used for autonomous speech recognition.

Each audio can be assigned with multiple sentence labels.

The structure of one sentence label is like::

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
            <key>: <value>
            ...
            ...
        }
    }



To create a :class:`~tensorbay.label.label_sentence.LabeledSentence` label:

    >>> from tensorbay.label import LabeledSentence
    >>> from tensorbay.label import Word
    >>> sentence_label = LabeledSentence(
    ... sentence=[Word("text", 1.1, 1.6)],
    ... spell=[Word("spell", 1.1, 1.6)],
    ... phone=[Word("phone", 1.1, 1.6)],
    ... attributes={"attribute_name": "attribute_value"}
    ... )
    >>> sentence_label
    LabeledSentence(
      (sentence): [
        Word(
          (text): 'text',
          (begin): 1.1,
          (end): 1.6
        )
      ],
      (spell): [
        Word(
          (text): 'text',
          (begin): 1.1,
          (end): 1.6
        )
      ],
      (phone): [
        Word(
          (text): 'text',
          (begin): 1.1,
          (end): 1.6
        )
      ],
      (attributes): {
        'attribute_name': 'attribute_value'
      }

Sentence.sentence
=================

The :attr:`~tensorbay.label.label_sentence.LabeledSentence.sentence` of a
:class:`~tensorbay.label.label_sentence.LabeledSentence` is a list of
:class:`~tensorbay.label.label_sentence.Word`,
representing the transcripted sentence of the audio.


Sentence.spell
==============

The :attr:`~tensorbay.label.label_sentence.LabeledSentence.spell` of a
:class:`~tensorbay.label.label_sentence.LabeledSentence` is a list of
:class:`~tensorbay.label.label_sentence.Word`,
representing the spell within the sentence.

It is only for Chinese language.

Sentence.phone
==============

The :attr:`~tensorbay.label.label_sentence.LabeledSentence.phone` of a
:class:`~tensorbay.label.label_sentence.LabeledSentence` is a list of
:class:`~tensorbay.label.label_sentence.Word`,
representing the phone of the sentence label.


Word
====

:class:`~tensorbay.label.label_sentence.Word` is the basic component of a phonetic transcription sentence,
containing the content of the word, the start and the end time in the audio.

    >>> from tensorbay.label import Word
    >>> Word("text", 1.1, 1.6)
    Word(
      (text): 'text',
      (begin): 1,
      (end): 2
    )

:attr:`~tensorbay.label.label_sentence.LabeledSentence.sentence`,
:attr:`~tensorbay.label.label_sentence.LabeledSentence.spell`,
and :attr:`~tensorbay.label.label_sentence.LabeledSentence.phone` of a sentence label all compose of
:class:`~tensorbay.label.label_sentence.Word`.

Sentence.attributes
===================

The attributes of the transcripted sentence.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

SentenceSubcatalog
==================

Before adding sentence labels to the dataset,
:class:`~tensorbay.label.label_sentence.SentenceSubcatalog` should be defined.

Besides :ref:`reference/label_format/CommonSubcatalogProperties:attributes information` in
:class:`~tensorbay.label.label_sentence.SentenceSubcatalog`,
it also has :attr:`~tensorbay.label.label_sentence.SentenceSubcatalog.is_sample`,
:attr:`~tensorbay.label.label_sentence.SentenceSubcatalog.sample_rate`
and :attr:`~tensorbay.label.label_sentence.SentenceSubcatalog.lexicon`.
to describe the transcripted sentences of the audio.

The catalog with only Sentence subcatalog is typically stored in a json file as follows::

    {
        "SENTENCE": {                                     <object>*
            "isSample":                                  <boolean>! -- Whether the unit of sampling points in Sentence label is the
                                                                       number of samples. The default value is false and the units
                                                                       are seconds.
            "sampleRate":                                 <number>  -- Audio sampling frequency whose unit is Hz. It is required
                                                                       when "isSample" is true.
            "description":                                <string>! -- Subcatalog description, (default: "").
            "attributes": [                                <array>  -- Attribute list, which contains all attribute information.
                {
                    "name":                               <string>* -- Attribute name.
                    "enum": [...],                         <array>  -- All possible options for the attribute.
                    "type":                      <string or array>  -- Type of the attribute including "boolean", "integer",
                                                                       "number", "string", "array" and "null". And it is not
                                                                       required when "enum" is provided.
                    "minimum":                            <number>  -- Minimum value of the attribute when type is "number".
                    "maximum":                            <number>  -- Maximum value of the attribute when type is "number".
                    "items": {                            <object>  -- Used only if the attribute type is "array".
                        "enum": [...],                     <array>  -- All possible options for elements in the attribute array.
                        "type":                  <string or array>  -- Type of elements in the attribute array.
                        "minimum":                        <number>  -- Minimum value of elements in the attribute array when type is
                                                                       "number".
                        "maximum":                        <number>  -- Maximum value of elements in the attribute array when type is
                                                                       "number".
                    },
                    "description":                        <string>! -- Attribute description, (default: "").
                },
                ...
                ...
            ]
            "lexicon": [                                   <array>  -- A list consists all of text and phone.
                [
                    text,                                 <string>  -- Word.
                    phone,                                <string>  -- Corresponding phonemes.
                    phone,                                <string>  -- Corresponding phonemes (A word can correspond to more than
                                                                       one phoneme).
                    ...
                ],
                ...
            ]
        }
    }

.. note::

   ``*`` indicates that the field is required. ``!`` indicates that the field has a default value.

Besides giving the parameters while initializing
:class:`~tensorbay.label.label_sentence.SentenceSubcatalog`,
it's also feasible to set them after initialization.

   >>> from tensorbay.label import SentenceSubcatalog
   >>> sentence_subcatalog = SentenceSubcatalog()
   >>> sentence_subcatalog.is_sample = True
   >>> sentence_subcatalog.sample_rate = 5
   >>> sentence_subcatalog.append_lexicon(["text", "spell", "phone"])
   >>> sentence_subcatalog
   SentenceSubcatalog(
     (is_sample): True,
     (sample_rate): 5,
     (lexicon): [...]
   )

To add a :class:`~tensorbay.label.label_sentence.LabeledSentence` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.sentence = []
    >>> data.label.sentence.append(sentence_label)

.. note::

   One data may contain multiple Sentence labels,
   so the :attr:`Data.label.sentence<tensorbay.dataset.data.Data.label.sentence>` must be a list.
