###########################
 Audio with sentence Label
###########################

:ref:`supported_label_types:Sentence` is one of the supported label types.
It represents Sentence label of audio data.

*************
 Preparation
*************

First of all, create a :ref:`features/tensorbay_client:GAS Client`.

.. code:: python

   >>> from graviti import GAS

   >>> ACCESS_KEY = "Accesskey-*****"
   >>> gas = GAS(ACCESS_KEY)

*****************************
 Read Dataset from TensorBay
*****************************

As mentioned in :ref:`quick_start:Quick Start`, obtain_ and fork_ should be done before reading a
dataset from TensorBay. Then, pass the correct dataset name to the GAS client, and you will get a
:ref:`features/tensorbay_client:Dataset Client`.

Here, we take `THCHS-30`_ as an example.

.. _fork: https://docs.graviti.cn/guide/opendataset/fork

.. _THCHS-30: https://www.graviti.cn/open-datasets/THCHS30

.. _obtain: https://docs.graviti.cn/guide/opendataset/get

.. code:: python

   >>> dataset_client = gas.get_dataset("THCHS-30")

If you are not sure about the dataset name, you can visit our `Opendataset Platform`_ to check all
"forkable" open datasets.

.. _opendataset platform: https://www.graviti.cn/open-datasets

You can use the list method to print all your forked open datasets.

.. code:: python

   >>> list(gas.list_dataset_names())
   ['Dogs vs. Cats', 'nuScenes', 'THCHS-30']

In :ref:`basic_concepts:Dataset` ``THCHS-30``, there are three :ref:`Segments <basic_concepts:Segment>` :
``"train"`` , ``"dev"`` and ``"test"``. The desired :ref:`basic_concepts:Segment` can be obtained by its unique name.
Take :ref:`basic_concepts:Segment` ``"dev"`` as an example, it could be obtained by:

.. code:: python

   >>> dev_segment = dataset_client.get_segment_object("dev")

The :ref:`basic_concepts:Segment` `"dev"` contains a sequence of :ref:`basic_concepts:Data`. 
You can get one by index.

.. code:: python

   >>> data = dev_segment[0]
   >>> data
   Data("tb:THCHS-30:dev://A11_101.wav")(
    (fileuri): tb:THCHS-30:dev://A11_101.wav,
    (labels): Labels(
        (sentence): [
            LabeledSentence(...)
            ]
        )
    )

.. note::

   If the :ref:`basic_concepts:Segment` or :ref:`basic_concepts:FusionSegment` is created without
   given name, then its name will be "".

In each :ref:`basic_concepts:Data`,
there is a sequence of :ref:`supported_label_types:Sentence` annotations.
You can get one by index.

.. code:: python

   >>> label_audio = data.labels.sentence[0]
   >>> label_audio
   LabeledSentence(
       (sentence): [
           Word(
            (text): '七十',
            (begin): 0,
            (end): 0
    )
    ...
    ],
       (spell): [
          Word(
            (text): 'qi1',
            (begin): 0,
            (end): 0
    )
    ...
    ],
        (phone): [
          Word(
            (text): 'q',
            (begin): 0,
            (end): 0
    )
    ...
    ],
        (attributes): None
   )

.. code:: python
    
    >>> label_audio.sentence
    [Word(
        (text): '七十',
        (begin): 0,
        (end): 0
    ),
        ...
        )
    ]

In ``sentence`` attribute of :ref:`supported_label_types:Sentence`,
there is a list of :ref:`supported_label_types:Word`.
In a Word instance, ``text`` means one phrase of a sentence, ``begin`` means the start time of text,
``end`` means the end time of text.

    >>> label_audio.spell
    [Word(
        (text): 'qi1',
        (begin): 0,
        (end): 0
    )
        ...
        )
    ]

In ``spell`` attribute of :ref:`supported_label_types:Sentence`,
there is a list of :ref:`supported_label_types:Word`.
In a Word instance, ``text`` means the Chinese Phonetic Alphabet with tone or English spelling
of a word.
'qi1' is the Chinese Phonetic Alphabet with first tone of '七'.
``begin`` means the start time of text, ``end`` means the end time of text.

    >>> label_audio.phone
    [Word(
        (text): 'q',
        (begin): 0,
        (end): 0
    )
        ...
        )
    ]

In ``phone`` attribute of :ref:`supported_label_types:Sentence`,
there is a list of :ref:`supported_label_types:Word`.
In a Word instance, ``text`` means the Chinese initials and finals or English phonemes of a word.
'q' is the Chinese initial of '七', ``begin`` means the start time of text,
``end`` means the end time of text.

The ``THCHS-30`` dataset only has one label type which is ``sentence``.

*************************
 Read Dataset from Local
*************************

If you want to read a dataset from local and there is an available :ref:`contribution:Dataloader`,
just import the loader function and pass the local dataset directory to it. The directory
structure for ``THCHS-30`` should be like:

.. code:: console
    
    <path>
        lm_word/
            lexicon.txt
        data/
            A11_0.wav.trn
            ...
        dev/
            A11_101.wav
            ...
        train/
        test/

.. code:: python

    >>> from graviti.opendataset import THCHS30

    >>> dataset = THCHS30("path/to/dataset/directory")
    >>> dataset
        Dataset("THCHS30") [
            Segment("") [...]
        ]

.. note::

   Note that ``THCHS30`` is not the name, but the :ref:`contribution:Identifier` of the dataset
   "THCHS-30". See :ref:`definition of identifier <contribution:Identifier>` for more details.

.. note::

   Note that :ref:`basic_concepts:Dataset` and :ref:`features/tensorbay_client:Dataset Client`
   are different concepts.

.. warning::

   TensorBay dataloader works well only with the original dataset directory structure.
   Downloading datasets from either official website or `Graviti Opendatset Platform`_ is highly
   recommended.

.. _graviti opendatset platform: https://www.graviti.cn/open-datasets

TensorBay supplies two methods to fetch :ref:`basic_concepts:Segment` from
:ref:`basic_concepts:Dataset`.

.. code:: python

   >>> dev_segment = dataset.get_segment_by_name("dev")

   >>> first_segment = dataset[0]

The :ref:`basic_concepts:Segment` you get now is the same as the one you read from TensorBay in the
:ref:`quick_start:Read Dataset from TensorBay` part.

**************************
 Write Dataset Dataloader
**************************

If there is no :ref:`contribution:Dataloader` avaliable to your target dataset,
welcome to write and contribute one.
Now we take ``THCHS-30`` as an example to explain how to write a dataloader for datasets with
:ref:`supported_label_types:Sentence` label.

Write the Catalog
=================

Before writing the dataloader for dataset, typically, we need to write a
:ref:`contribution:Catalog`. Catalog is a json file contains all label information of one dataset.
See :ref:`this page <basic_concepts:Catalog & SubCatalog>` for more details. 
However the catalog of ``THCHS-30`` is too large, so we need to load the subcatalog by raw file
and map it to catalog, See :ref:`code block <THCHS30-dataloader>` below for more details.

Write the Dataloader
====================

The function of :ref:`contribution:Dataloader` is to read the dataset into a
:ref:`basic_concepts:Dataset` object.
The :ref:`code block <THCHS30-dataloader>` below displays the ``THCHS-30`` dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/THCHS30/loader.py
   :language: python
   :name: THCHS30-dataloader
   :linenos:
   :emphasize-lines: 13-15,40

There are mainly two steps to write a :ref:`contribution:Dataloader`:

-  Create a :ref:`basic_concepts:Dataset` and its relevant :ref:`Segments <basic_concepts:Segment>`.
-  Add the :ref:`basic_concepts:Data` and corresponding labels
   to the created :ref:`Segments <basic_concepts:Segment>`.

Create Dataset and Segments
---------------------------

Note that after creating the :ref:`basic_concepts:Dataset`,
you need to load the :ref:`contribution:Catalog`.(L40)
The catalog file ``catalog.json`` is in the same directory with dataloader file.

In this example, there is no ``catalog.json`` file, because the lexion of ``THCHS-30`` is too
large. The lexion is a list of dictionary lists. Therefore, We need to load subcatalog from the raw
file and map it to have the catalog.(L57-63)

Add Data and Labels
-------------------

It takes four key substeps to add the data and the labels:

-  Creating :ref:`basic_concepts:Data` and adding content.
-  Creating :ref:`supported_label_types:Sentence` and adding annotations.
-  Appending the Sentence labels to the created Data.
-  Appending the Data to the created Segment.

See :ref:`this page <supported_label_types:Sentence>` for more details for about Sentence annoation
details.

.. note::
   The :ref:`THCHS-30 dataloader <THCHS30-dataloader>` above uses relative import(L13-15).
   However, when you write your own dataloader you should use regular import as shown below.
   And when you want to contribute your own dataloader, remember to use relative import.

.. code:: python

   >>> from graviti.dataset import Data, Dataset
   >>> from graviti.label import LabeledSentence, SentenceSubcatalog, Word

***********************************
 Upload Local Dataset to TensorBay
***********************************

Once you write your own :ref:`contribution:Dataloader` and read the local dataset into a
:ref:`basic_concepts:Dataset` object, you can upload it to TensorBay and share with the community.

.. code:: python

   >>> dataset = gas.create("THCHS-30")
   >>> dataset_client = gas.upload_dataset_object(dataset, jobs=8, skip_uploaded_files=False)
   >>> dataset_client.commit("THCHS-30")

Remember to execute the :ref:`features/version_control:Commit` step after uploading.
If needed, you can re-upload and commit again.
Please see :ref:`features/version_control:Version Control` for more details.

.. note::

   Commit operation can alse be done on our GAS_ Platform.

.. _gas: https://www.graviti.cn/tensorBay

Please see :ref:`contribution:Contribution` for how to contribute your dataloader.
