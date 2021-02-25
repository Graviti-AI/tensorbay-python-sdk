#######################
 Supported Label Types
#######################

TensorBay supports multiple types of labels.

Each :class:`~tensorbay.dataset.data.Data` object
can have multiple types of :class:`labels<tensorbay.dataset.data.Labels>`.

And each type of :class:`labels<tensorbay.dataset.data.Labels>` is supported with a specific label
class,
and has a corresponding :ref:`subcatalog<basic_concepts:Catalog & Subcatalog>` class.

.. table:: supported label types
   :widths: auto

   ===========================================  ==================================================  =============================================================
   supported label types                          label classes                                       subcatalog classes
   ===========================================  ==================================================  =============================================================
   :ref:`supported_label_types:Classification`  :class:`~tensorbay.label.label.Classification`      :class:`~tensorbay.label.subcatalog.ClassificationSubcatalog`
   :ref:`supported_label_types:Box2D`           :class:`~tensorbay.label.label.LabeledBox2D`        :class:`~tensorbay.label.subcatalog.Box2DSubcatalog`
   :ref:`supported_label_types:Box3D`           :class:`~tensorbay.label.label.LabeledBox3D`        :class:`~tensorbay.label.subcatalog.Box3DSubcatalog`
   :ref:`supported_label_types:Keypoints2D`     :class:`~tensorbay.label.label.LabeledKeypoints2D`  :class:`~tensorbay.label.subcatalog.Keypoints2DSubcatalog`
   :ref:`supported_label_types:Sentence`        :class:`~tensorbay.label.label.LabeledSentence`     :class:`~tensorbay.label.subcatalog.SentenceSubcatalog`
   ===========================================  ==================================================  =============================================================

*************************
 Common Label Properties
*************************

Different types of labels contain differenct aspects of annotation information about the data.
Some are more general, and some are unique to a specific label type.

We first introduce three common properties of a label,
and the unique ones will be explained under the corresponding type of label.

Here we take a :ref:`2D box label <supported_label_types:Box2D>` as an example:

.. code:: python

    >>> from tensorbay.label import LabeledBox2D
    >>> label = LabeledBox2D(
    ... 10, 20, 30, 40,
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )

Category
========

Category is a string indicating the class of the labeled object.

.. code:: python

    >>> label.category
    'data_category'

Attributes
==========

Attributes are the additional information about this data,
and there is no limit on the number of attributes.

The attribute names and values are stored in key-value pairs.

.. code:: python

   >>> label.attributes
   {'attribute_name': 'attribute_value'}


Instance
========

Instance is the unique id for the object inside of the label,
which is mostly used for tracking tasks.

.. code:: python

   >>> label.instance
   "instance_ID"

******************************
 Common Subcatalog Properties
******************************

Before creating a label or adding a label to data,
you need to define the annotation rules of the specific label type inside the dataset,
which is subcatalog.

Different label types have different subcatalog classes.

Here we take :class:`~tensorbay.label.subcatalog.Box2DSubcatalog` as an example
to describe some common features of subcatalog.

.. code:: python

   >>> from tensorbay.label import Box2DSubcatalog
   >>> box2d_subcatalog = Box2DSubcatalog(is_tracking=True)

TrackingInformation
===================

If the label of this type in the dataset has the information of instance IDs,
then the subcatalog should set a flag to show its support for tracking information.

You can pass ``True`` to the ``is_tracking`` parameter while creating the subcatalog,
or you can set the ``is_tracking`` attr after initialization.

.. code:: python

   >>> box2d_subcatalog.is_tracking = True

CategoryInformation
===================

If the label of this type in the dataset has category,
then the subcatalog should contain all the optional categories.

Each :ref:`category<supported_label_types:Category>` of a label
appeared in the dataset should be within the categories of the subcatalog.

You can add category information to the subcatalog.

.. code:: python

    >>> box2d_subcatalog.add_category(name="cat", description="The Flerken")
    >>> box2d_subcatalog.categories
    NameOrderedDict {
      'cat': CategoryInfo("cat")
    }

We use :class:`~tensorbay.label.supports.CategoryInfo` to describe
a :ref:`category<supported_label_types:Category>`.
See details in :class:`~tensorbay.label.supports.CategoryInfo`.

AttributesInformation
=====================

If the label of this type in the dataset has attributes,
then the subcatalog should contain all the rules for different attributes.

Each :ref:`attribute<supported_label_types:Attributes>` of a label
appeared in the dataset should follow the rules set in the attributes of the subcatalog.

You can add attribute information to the subcatalog.

.. code:: python

    >>> box2d_subcatalog.add_attribute(
    ... name="attribute_name",
    ... type_="number",
    ... maximum=100,
    ... minimum=0,
    ... description="attribute description"
    ... )
    >>> box2d_subcatalog.categories
    NameOrderedDict {
      'attribute_name': AttributeInfo("attribute_name")(...)
    }

We use :class:`~tensorbay.label.attributes.AttributeInfo` to describe the rules of an
:ref:`attribute<supported_label_types:Attributes>`, which refers to the `Json schema`_ method.

See details in :class:`~tensorbay.label.attributes.AttributeInfo`.

.. _Json schema: https://json-schema.org/

Other unique subcatalog features will be explained in the corresponding label type section.

****************
 Classification
****************

Classification is to classify data into different categories.

It is the annotation for the entire file,
so each data can only be assigned with one classification label.

Classification labels applies to different types of data, such as images and texts.

The structure of one classification label is like::

        {
            "category": <str>
            "attributes": {
                <key>: <value>
                ...
                ...
            }
        }



To create a :class:`~tensorbay.label.label.Classification` label:

.. code:: python

    >>> from tensorbay.label import Classification
    >>> classification_label = Classification(
    ... category="data_category",
    ... attributes={"attribute_name": "attribute_value"}
    ... )
    >>> classification_label
    Classification(
      (category): 'data_category',
      (attributes): {...}
    )


Classification.Category
=======================

The category of the entire data file.
See :ref:`supported_label_types:Category` for details.

Classification.Attributes
=========================

The attributes of the entire data file.
See :ref:`supported_label_types:Attributes` for details.

.. note::

   There must be either a category or attributes in one classification label.

ClassificationSubcatalog
========================

Before adding the classification label to data,
:class:`~tensorbay.label.subcatalog.ClassificationSubcatalog` should be defined.

:class:`~tensorbay.label.subcatalog.ClassificationSubcatalog`
has categories and attributes information,
see :ref:`supported_label_types:CategoryInformation` and
:ref:`supported_label_types:AttributesInformation` for details.

To add a :class:`~tensorbay.label.label.Classification` label to one data:

.. code:: python

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.labels.classification = classification_label

.. note::

   One data can only have one classification label.

*******
 Box2D
*******

Box2D is a type of label with a 2D bounding box on an image.
It's usually used for object detection task.

Each data can be assigned with multiple Box2D label.

The structure of one Box2D label is like::

    {
        "box2d": {
            "xmin": <float>
            "ymin": <float>
            "xmax": <float>
            "ymax": <float>
        },
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        },
        "instance": <str>
    }

To create a :class:`~tensorbay.label.label.LabeledBox2D` label:

.. code:: python

    >>> from tensorbay.label import LabeledBox2D
    >>> box2d_label = LabeledBox2D(
    ... xmin, ymin, xmax, ymax,
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> box2d_label
    LabeledBox2D(xmin, ymin, xmax, ymax)(
      (category): 'category',
      (attributes): {...}
      (instance): 'instance_ID'
    )

Box2D.box2d
===========

:class:`~tensorbay.label.label.LabeledBox2D` extends :class:`~tensorbay.geometry.box.Box2D`.

To construct a :class:`~tensorbay.label.label.LabeledBox2D` instance with only the geometry
information,
you can use the coordinates of the top-left and bottom-right vertexes of the 2D bounding box,
or you can use the coordinate of the top-left vertex, the height and the width of the bounding box.

.. code:: python

    >>> LabeledBox2D(10, 20, 30, 40)
    LabeledBox2D(10, 20, 30, 40)()
    >>> LabeledBox2D(x=10, y=20, width=20, height=20)
    LabeledBox2D(10, 20, 30, 40)()

It contains the basic geometry information of the 2D bounding box.

.. code:: python

    >>> box2d_label.xmin
    10
    >>> box2d_label.ymin
    20
    >>> box2d_label.xmax
    30
    >>> box2d_label.ymax
    40
    >>> box2d_label.br
    Vector2D(30, 40)
    >>> box2d_label.tl
    Vector2D(10, 20)
    >>> box2d_label.area()
    400

Box2D.Category
==============

The category of the object inside the 2D bounding box.
See :ref:`supported_label_types:Category` for details.

Box2D.Attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`supported_label_types:Attributes` for details.

Box2D.Instance
==============

Instance is the unique ID for the object inside of the 2D bounding box,
which is mostly used for tracking tasks.
See :ref:`supported_label_types:Instance` for details.

Box2DSubcatalog
===============

Before adding the Box2D labels to data,
:class:`~tensorbay.label.subcatalog.Box2DSubcatalog` should be defined.

:class:`~tensorbay.label.subcatalog.Box2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`supported_label_types:CategoryInformation`,
:ref:`supported_label_types:AttributesInformation` and
:ref:`supported_label_types:TrackingInformation` for details.

To add a :class:`~tensorbay.label.label.LabeledBox2D` label to one data:

.. code:: python

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.labels.box2d = []
    >>> data.labels.box2d.append(box2d_label)

.. note::

   One data may contain multiple Box2D labels,
   so the :attr:`Data.labels.box2d<tensorbay.dataset.data.Data.labels.box2d>` must be a list.

*******
 Box3D
*******

Box3D is a type of label with a 3D bounding box on point cloud,
which is often used for 3D object detection.

Currently, Box3D labels applies to point data only.

Each point cloud can be assigned with multiple Box3D label.

The structure of one Box3D label is like::

    {
        "box3d": {
            "translation": {
                "x": <float>
                "y": <float>
                "z": <float>
            },
            "rotation": {
                "w": <float>
                "x": <float>
                "y": <float>
                "z": <float>
            },
            "size": {
                "x": <float>
                "y": <float>
                "z": <float>
            }
        },
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        },
        "instance": <str>
    }

To create a :class:`~tensorbay.label.label.LabeledBox3D` label:

.. code:: python

    >>> from tensorbay.label import LabeledBox3D
    >>> box3d_label = LabeledBox3D(
    ... translation=[0, 0, 0],
    ... rotation=[1, 0, 0, 0],
    ... size=[10, 20, 30],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> box3d_label
    LabeledBox3D(
      (translation): Vector3D(0, 0, 0),
      (rotation): Quaternion(1.0, 0.0, 0.0, 0.0),
      (size): Vector3D(10, 20, 30),
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )


Box3D.box3d
===========

:class:`~tensorbay.label.label.LabeledBox3D` extends :class:`~tensorbay.geometry.box.Box3D`.

To construct a :class:`~tensorbay.label.label.LabeledBox3D` instance with only the geometry
information,
you can use the transform matrix and the size of the 3D bounding box,
or you can use translation and rotation to represent the transform of the 3D bounding box.

.. code:: python

    >>> LabeledBox3D(
    ... [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
    ... size=[10, 20, 30],
    ... )
    LabeledBox3D(
      (translation): Vector3D(0, 0, 0),
      (rotation): Quaternion(1.0, -0.0, -0.0, -0.0),
      (size): Vector3D(10, 20, 30)
    )
    >>> LabeledBox3D(
    ... translation=[0, 0, 0],
    ... rotation=[1, 0, 0, 0],
    ... size=[10, 20, 30],
    ... )
    LabeledBox3D(
      (translation): Vector3D(0, 0, 0),
      (rotation): Quaternion(1.0, 0.0, 0.0, 0.0),
      (size): Vector3D(10, 20, 30)
    )

It contains the basic geometry information of the 3D bounding box.

.. code:: python

    >>> box3d_label.transform
    Transform3D(
      (translation): Vector3D(0, 0, 0),
      (rotation): Quaternion(1.0, 0.0, 0.0, 0.0)
    )
    >>> box3d_label.translation
    Vector3D(0, 0, 0)
    >>> box3d_label.rotation
    Quaternion(1.0, 0.0, 0.0, 0.0)
    >>> box3d_label.size
    Vector3D(10, 20, 30)
    >>> box3d_label.volumn()
    6000

Box3D.Category
==============

The category of the object inside the 3D bounding box.
See :ref:`supported_label_types:Category` for details.

Box3D.Attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`supported_label_types:Attributes` for details.

Box3D.Instance
==============

Instance is the unique id for the object inside of the 3D bounding box,
which is mostly used for tracking tasks.
See :ref:`supported_label_types:Instance` for details.

Box3DSubcatalog
===============

Before adding the Box2D labels to data,
:class:`~tensorbay.label.subcatalog.Box2DSubcatalog` should be defined.

:class:`~tensorbay.label.subcatalog.Box2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`supported_label_types:CategoryInformation`,
:ref:`supported_label_types:AttributesInformation` and
:ref:`supported_label_types:TrackingInformation` for details.

To add a :class:`~tensorbay.label.label.LabeledBox3D` label to one data:

.. code:: python

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.labels.box3d = []
    >>> data.labels.box3d.append(box3d_label)

.. note::

   One data may contain multiple Box3D labels,
   so the :attr:`Data.labels.box3d<tensorbay.dataset.data.Data.labels.box3d>` must be a list.

*************
 Keypoints2D
*************

Keypoints2D is a type of label with a set of 2D keypoints.
It is often used for animal and human pose estimation.

Keypoints2D labels mostly applies to images.

Each data can be assigned with multiple Keypoints2D labels.

The structure of one Keypoints2D label is like::

    {
        "keypoints2d": [
            { "x": <float>
              "y": <float>
              "v": <int>
            },
            ...
            ...
        ],
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        },
        "instance": <str>
    }

To create a :class:`~tensorbay.label.label.LabeledKeypoints2D` label:

.. code:: python

    >>> from tensorbay.label import LabeledKeypoints2D
    >>> keypoints2d_label = LabeledKeypoints2D(
    ... [[10, 20], [15, 25], [20, 30]],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> keypoints2d_label
    LabeledKeypoints2D [
      Keypoint2D(10, 20),
      Keypoint2D(15, 25),
      Keypoint2D(20, 30)
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )

Keypoints2D.keypoints2d
=======================

:class:`~tensorbay.label.label.LabeledKeypoints2D` extends
:class:`~tensorbay.geometry.box.Keypoints2D`.

To construct a :class:`~tensorbay.label.label.LabeledKeypoints2D` instance with only the geometry
information,
you need the coordinates of the set of 2D keypoints.
You can also add the visible status of each 2D keypoint.

.. code:: python

    >>> LabeledKeypoints2D([[10, 20], [15, 25], [20, 30]])
    LabeledKeypoints2D [
      Keypoint2D(10, 20),
      Keypoint2D(15, 25),
      Keypoint2D(20, 30)
    ]()
    >>> LabeledKeypoints2D([[10, 20, 0], [15, 25, 1], [20, 30, 1]])
    LabeledKeypoints2D [
      Keypoint2D(10, 20, 0),
      Keypoint2D(15, 25, 1),
      Keypoint2D(20, 30, 1)
    ]()

It contains the basic geometry information of the 2D keypoints.
And you can access the keypoints by index.

.. code:: python

    >>> keypoints2d_label[0]
    Keypoint2D(10, 20)

Keypoints2D.Category
====================

The category of the object inside the 3D bounding box.
See :ref:`supported_label_types:Category` for details.

Keypoints2D.Attributes
======================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`supported_label_types:Attributes` for details.

Keypoints2D.Instance
====================

Instance is the unique ID for the object inside of the 3D bounding box,
which is mostly used for tracking tasks.
See :ref:`supported_label_types:Instance` for details.

Keypoints2DSubcatalog
=====================

Before adding 2D keypoints labels to the dataset,
:class:`~tensorbay.label.subcatalog.Keypoints2DSubcatalog` should be defined.

Besides :ref:`supported_label_types:AttributesInformation`,
:ref:`supported_label_types:CategoryInformation`,
:ref:`supported_label_types:TrackingInformation` in
:class:`~tensorbay.label.subcatalog.Keypoints2DSubcatalog`,
it also has :attr:`~tensorbay.label.subcatalog.Keypoints2DSubcatalog.keypoints`
to describe a set of keypoints corresponding to certain categories.

.. code:: python

   >>> from tensorbay.label import Keypoints2DSubcatalog
   >>> keypoints2d_subcatalog = Keypoints2DSubcatalog()
   >>> keypoints2d_subcatalog.add_keypoints(
   ... 3,
   ... names=["head", "body", "feet"],
   ... skeleton=[[0, 1], [1, 2]],
   ... visible="BINARY",
   ... parent_categories=["cat"],
   ... description="keypoints of cats"
   ... )
   >>> keypoints2d_subcatalog.keypoints
   [KeypointsInfo(
      (number): 3,
      (names): [...],
      (skeleton): [...],
      (visible): 'BINARY',
      (parent_categories): [...]
    )]

We use :class:`~tensorbay.label.supports.KeypointsInfo` to describe a set of 2D keypoints.

The first parameter of :meth:`~tensorbay.label.subcatalog.Keypoints2DSubcatalog.add_keypoints`
is the number of the set of 2D keypoints, which is required.

The ``names`` is a list of string representing the names for each 2D keypoint,
the length of which is consistent with the number.

The ``skeleton`` is a two-dimensional list indicating the connection between the keypoints.

The ``visible`` is the visible status that limits the
:attr:`~tensorbay.geometry.keypoint.Keypoint2D.v`
of :class:`~tensorbay.geometry.keypoint.Keypoint2D`.
It can only be "BINARY" or "TERNARY".

See details in :class:`~tensorbay.geometry.keypoint.Keypoint2D`.

The ``parent_categories`` is a list of categories indicating to which category the keypoints rule
applies.

Mostly, ``parent_categories`` is not given,
which means the keypoints rule applies to all the categories of the entire dataset.

To add a :class:`~tensorbay.label.label.LabeledKeypoints2D` label to one data:

.. code:: python

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.labels.keypoints2d = []
    >>> data.labels.keypoints2d.append(keypoints2d_label)

.. note::

   One data may contain multiple Keypoints2D labels,
   so the :attr:`Data.labels.keypoints2d<tensorbay.dataset.data.Data.labels.keypoints2d>`
   must be a list.


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
            <key>: <value>,
            ...
            ...
        }
    }



To create a :class:`~tensorbay.label.label.LabeledSentence` label:

.. code:: python

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

The :attr:`~tensorbay.label.label.LabeledSentence.sentence` of a
:class:`~tensorbay.label.label.LabeledSentence` is a list of
:class:`~tensorbay.label.label.Word`,
representing the transcripted sentence of the audio.


Sentence.spell
==============

The :attr:`~tensorbay.label.label.LabeledSentence.spell` of a
:class:`~tensorbay.label.label.LabeledSentence` is a list of
:class:`~tensorbay.label.label.Word`,
representing the spell within the sentence.

It is only for Chinese language.

Sentence.phone
==============

The :attr:`~tensorbay.label.label.LabeledSentence.phone` of a
:class:`~tensorbay.label.label.LabeledSentence` is a list of
:class:`~tensorbay.label.label.Word`,
representing the phone of the sentence label.


Word
====

:class:`~tensorbay.label.label.Word` is the basic component of a phonetic transcription sentence,
containing the content of the word, the start and the end time in the audio.

.. code:: python

    >>> from tensorbay.label import Word
    >>> Word("text", 1.1, 1.6)
    Word(
      (text): 'text',
      (begin): 1,
      (end): 2
    )

:attr:`~tensorbay.label.label.LabeledSentence.sentence`,
:attr:`~tensorbay.label.label.LabeledSentence.spell`,
and :attr:`~tensorbay.label.label.LabeledSentence.phone` of a sentence label all compose of
:class:`~tensorbay.label.label.Word`.

Sentence.Attributes
===================

The attributes of the transcripted sentence.
See :ref:`supported_label_types:AttributesInformation` for details.

SentenceSubcatalog
==================

Before adding sentence labels to the dataset,
:class:`~tensorbay.label.subcatalog.SentenceSubcatalog` should be defined.

Besides :ref:`supported_label_types:AttributesInformation` in
:class:`~tensorbay.label.subcatalog.SentenceSubcatalog`,
it also has :attr:`~tensorbay.label.subcatalog.SentenceSubcatalog.is_sample`,
:attr:`~tensorbay.label.subcatalog.SentenceSubcatalog.sample_rate`
and :attr:`~tensorbay.label.subcatalog.SentenceSubcatalog.lexicon`.
to describe the transcripted sentences of the audio.

.. code:: python

   >>> from tensorbay.label import SentenceSubcatalog
   >>> sentence_subcatalog = SentenceSubcatalog(
   ... is_sample=True,
   ... sample_rate=5,
   ... lexicon=[["word", "spell", "phone"]]
   ... )
   >>> sentence_subcatalog
   SentenceSubcatalog(
     (is_sample): True,
     (sample_rate): 5,
     (lexicon): [...]
   )
   >>> sentence_subcatalog.lexicon
   [['word', 'spell', 'phone']]

The ``is_sample`` is a boolen value indicating whether time format is sample related.

The ``sample_rate`` is the number of samples of audio carried per second.
If ``is_sample`` is Ture, then ``sample_rate`` must be provided.

The ``lexicon`` is a list consists all of text and phone.

Besides giving the parameters while initialing
:class:`~tensorbay.label.subcatalog.SentenceSubcatalog`,
you can set them after intialization.

.. code:: python

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

To add a :class:`~tensorbay.label.label.LabeledSentence` label to one data:

.. code:: python

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.labels.sentence = []
    >>> data.labels.sentence.append(sentence_label)

.. note::

   One data may contain multiple Sentence labels,
   so the :attr:`Data.labels.sentence<tensorbay.dataset.data.Data.labels.sentence>` must be a list.
