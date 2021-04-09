##############
 Label Format
##############

TensorBay supports multiple types of labels.

Each :class:`~tensorbay.dataset.data.Data` object
can have multiple types of :class:`label <~tensorbay.label.basic.Label>`.

And each type of :class:`label <~tensorbay.label.basic.Label>` is supported with a specific label
class,
and has a corresponding :ref:`subcatalog <reference/dataset_structure:Catalog>` class.

.. table:: supported label types
   :widths: auto

   ============================================  =============================================================  =======================================================================
   supported label types                           label classes                                                  subcatalog classes
   ============================================  =============================================================  =======================================================================
   :ref:`reference/label_format:Classification`  :class:`~tensorbay.label.label_classification.Classification`  :class:`~tensorbay.label.label_classification.ClassificationSubcatalog`
   :ref:`reference/label_format:Box2D`           :class:`~tensorbay.label.label_box.LabeledBox2D`               :class:`~tensorbay.label.label_box.Box2DSubcatalog`
   :ref:`reference/label_format:Box3D`           :class:`~tensorbay.label.label_box.LabeledBox3D`               :class:`~tensorbay.label.label_box.Box3DSubcatalog`
   :ref:`reference/label_format:Keypoints2D`     :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D`   :class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog`
   :ref:`reference/label_format:Sentence`        :class:`~tensorbay.label.label_sentence.LabeledSentence`       :class:`~tensorbay.label.label_sentence.SetenceSubcatalog`
   ============================================  =============================================================  =======================================================================

*************************
 Common Label Properties
*************************

Different types of labels contain differenct aspects of annotation information about the data.
Some are more general, and some are unique to a specific label type.

Three common properties of a label will be introduced first,
and the unique ones will be explained under the corresponding type of label.

Take a :ref:`2D box label <reference/label_format:Box2D>` as an example:

    >>> from tensorbay.label import LabeledBox2D
    >>> label = LabeledBox2D(
    ... 10, 20, 30, 40,
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> label
    LabeledBox2D(10, 20, 30, 40)(
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )

Category
========

Category is a string indicating the class of the labeled object.

    >>> label.category
    'data_category'

Attributes
==========

Attributes are the additional information about this data,
and there is no limit on the number of attributes.

The attribute names and values are stored in key-value pairs.

   >>> label.attributes
   {'attribute_name': 'attribute_value'}


Instance
========

Instance is the unique id for the object inside of the label,
which is mostly used for tracking tasks.

   >>> label.instance
   "instance_ID"

******************************
 Common Subcatalog Properties
******************************

Before creating a label or adding a label to data,
it's necessary to define the annotation rules of the specific label type inside the dataset.
This task is done by subcatalog.

Different label types have different subcatalog classes.

Take :class:`~tensorbay.label.label_box.Box2DSubcatalog` as an example
to describe some common features of subcatalog.

   >>> from tensorbay.label import Box2DSubcatalog
   >>> box2d_subcatalog = Box2DSubcatalog(is_tracking=True)
   >>> box2d_subcatalog
   Box2DSubcatalog(
      (is_tracking): True
   )

TrackingInformation
===================

If the label of this type in the dataset has the information of instance IDs,
then the subcatalog should set a flag to show its support for tracking information.

Pass ``True`` to the ``is_tracking`` parameter while creating the subcatalog,
or set the ``is_tracking`` attr after initialization.

   >>> box2d_subcatalog.is_tracking = True

CategoryInformation
===================

If the label of this type in the dataset has category,
then the subcatalog should contain all the optional categories.

Each :ref:`category<reference/label_format:Category>` of a label
appeared in the dataset should be within the categories of the subcatalog.

Category information can be added to the subcatalog.

    >>> box2d_subcatalog.add_category(name="cat", description="The Flerken")
    >>> box2d_subcatalog.categories
    NameOrderedDict {
      'cat': CategoryInfo("cat")
    }

:class:`~tensorbay.label.supports.CategoryInfo` is used to describe
a :ref:`category<reference/label_format:Category>`.
See details in :class:`~tensorbay.label.supports.CategoryInfo`.

AttributesInformation
=====================

If the label of this type in the dataset has attributes,
then the subcatalog should contain all the rules for different attributes.

Each :ref:`attribute<reference/label_format:Attributes>` of a label
appeared in the dataset should follow the rules set in the attributes of the subcatalog.

Attribute information ca be added to the subcatalog.

    >>> box2d_subcatalog.add_attribute(
    ... name="attribute_name",
    ... type_="number",
    ... maximum=100,
    ... minimum=0,
    ... description="attribute description"
    ... )
    >>> box2d_subcatalog.attributes
    NameOrderedDict {
      'attribute_name': AttributeInfo("attribute_name")(...)
    }

:class:`~tensorbay.label.attributes.AttributeInfo` is used to describe the rules of an
:ref:`attribute<reference/label_format:Attributes>`, which refers to the `Json schema`_ method.

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



To create a :class:`~tensorbay.label.label_classification.Classification` label:

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
See :ref:`reference/label_format:Category` for details.

Classification.Attributes
=========================

The attributes of the entire data file.
See :ref:`reference/label_format:Attributes` for details.

.. note::

   There must be either a category or attributes in one classification label.

ClassificationSubcatalog
========================

Before adding the classification label to data,
:class:`~tensorbay.label.label_classification.ClassificationSubcatalog` should be defined.

:class:`~tensorbay.label.label_classification.ClassificationSubcatalog`
has categories and attributes information,
see :ref:`reference/label_format:CategoryInformation` and
:ref:`reference/label_format:AttributesInformation` for details.

To add a :class:`~tensorbay.label.label_classification.Classification` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.classification = classification_label

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

To create a :class:`~tensorbay.label.label_box.LabeledBox2D` label:

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

:class:`~tensorbay.label.label_box.LabeledBox2D` extends :class:`~tensorbay.geometry.box.Box2D`.

To construct a :class:`~tensorbay.label.label_box.LabeledBox2D` instance with only the geometry
information,
use the coordinates of the top-left and bottom-right vertexes of the 2D bounding box,
or the coordinate of the top-left vertex, the height and the width of the bounding box.

    >>> LabeledBox2D(10, 20, 30, 40)
    LabeledBox2D(10, 20, 30, 40)()
    >>> LabeledBox2D(x=10, y=20, width=20, height=20)
    LabeledBox2D(10, 20, 30, 40)()

It contains the basic geometry information of the 2D bounding box.

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
See :ref:`reference/label_format:Category` for details.

Box2D.Attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:Attributes` for details.

Box2D.Instance
==============

Instance is the unique ID for the object inside of the 2D bounding box,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:Instance` for details.

Box2DSubcatalog
===============

Before adding the Box2D labels to data,
:class:`~tensorbay.label.label_box.Box2DSubcatalog` should be defined.

:class:`~tensorbay.label.label_box.Box2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:CategoryInformation`,
:ref:`reference/label_format:AttributesInformation` and
:ref:`reference/label_format:TrackingInformation` for details.

To add a :class:`~tensorbay.label.label_box.LabeledBox2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.box2d = []
    >>> data.label.box2d.append(box2d_label)

.. note::

   One data may contain multiple Box2D labels,
   so the :attr:`Data.label.box2d<tensorbay.dataset.data.Data.label.box2d>` must be a list.

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

To create a :class:`~tensorbay.label.label_box.LabeledBox3D` label:

    >>> from tensorbay.label import LabeledBox3D
    >>> box3d_label = LabeledBox3D(
    ... size=[10, 20, 30],
    ... translation=[0, 0, 0],
    ... rotation=[1, 0, 0, 0],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> box3d_label
    LabeledBox3D(
      (size): Vector3D(10, 20, 30),
      (translation): Vector3D(0, 0, 0),
      (rotation): quaternion(1.0, 0.0, 0.0, 0.0),
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )


Box3D.box3d
===========

:class:`~tensorbay.label.label_box.LabeledBox3D` extends :class:`~tensorbay.geometry.box.Box3D`.

To construct a :class:`~tensorbay.label.label_box.LabeledBox3D` instance with only the geometry
information,
use the transform matrix and the size of the 3D bounding box,
or use translation and rotation to represent the transform of the 3D bounding box.

    >>> LabeledBox3D(
    ... size=[10, 20, 30],
    ... transform_matrix=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
    ... )
    LabeledBox3D(
      (size): Vector3D(10, 20, 30)
      (translation): Vector3D(0, 0, 0),
      (rotation): quaternion(1.0, -0.0, -0.0, -0.0),
    )
    >>> LabeledBox3D(
    ... size=[10, 20, 30],
    ... translation=[0, 0, 0],
    ... rotation=[1, 0, 0, 0],
    ... )
    LabeledBox3D(
      (size): Vector3D(10, 20, 30)
      (translation): Vector3D(0, 0, 0),
      (rotation): quaternion(1.0, 0.0, 0.0, 0.0),
    )

It contains the basic geometry information of the 3D bounding box.

    >>> box3d_label.transform
    Transform3D(
      (translation): Vector3D(0, 0, 0),
      (rotation): quaternion(1.0, 0.0, 0.0, 0.0)
    )
    >>> box3d_label.translation
    Vector3D(0, 0, 0)
    >>> box3d_label.rotation
    quaternion(1.0, 0.0, 0.0, 0.0)
    >>> box3d_label.size
    Vector3D(10, 20, 30)
    >>> box3d_label.volumn()
    6000

Box3D.Category
==============

The category of the object inside the 3D bounding box.
See :ref:`reference/label_format:Category` for details.

Box3D.Attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:Attributes` for details.

Box3D.Instance
==============

Instance is the unique id for the object inside of the 3D bounding box,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:Instance` for details.

Box3DSubcatalog
===============

Before adding the Box3D labels to data,
:class:`~tensorbay.label.label_box.Box3DSubcatalog` should be defined.

:class:`~tensorbay.label.label_box.Box3DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:CategoryInformation`,
:ref:`reference/label_format:AttributesInformation` and
:ref:`reference/label_format:TrackingInformation` for details.

To add a :class:`~tensorbay.label.label_box.LabeledBox3D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.box3d = []
    >>> data.label.box3d.append(box3d_label)

.. note::

   One data may contain multiple Box3D labels,
   so the :attr:`Data.label.box3d<tensorbay.dataset.data.Data.label.box3d>` must be a list.

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

To create a :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D` label:

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

:class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D` extends
:class:`~tensorbay.geometry.box.Keypoints2D`.

To construct a :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D` instance with only the geometry
information,
The coordinates of the set of 2D keypoints are necessary.
The visible status of each 2D keypoint is optional.

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

It contains the basic geometry information of the 2D keypoints,
which can be obtained by index.

    >>> keypoints2d_label[0]
    Keypoint2D(10, 20)

Keypoints2D.Category
====================

The category of the object inside the 2D keypoints.
See :ref:`reference/label_format:Category` for details.

Keypoints2D.Attributes
======================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:Attributes` for details.

Keypoints2D.Instance
====================

Instance is the unique ID for the object inside of the 2D keypoints,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:Instance` for details.

Keypoints2DSubcatalog
=====================

Before adding 2D keypoints labels to the dataset,
:class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog` should be defined.

Besides :ref:`reference/label_format:AttributesInformation`,
:ref:`reference/label_format:CategoryInformation`,
:ref:`reference/label_format:TrackingInformation` in
:class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog`,
it also has :attr:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog.keypoints`
to describe a set of keypoints corresponding to certain categories.

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

:class:`~tensorbay.label.supports.KeypointsInfo` is used to describe a set of 2D keypoints.

The first parameter of :meth:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog.add_keypoints`
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

To add a :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.keypoints2d = []
    >>> data.label.keypoints2d.append(keypoints2d_label)

.. note::

   One data may contain multiple Keypoints2D labels,
   so the :attr:`Data.label.keypoints2d<tensorbay.dataset.data.Data.label.keypoints2d>`
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

Sentence.Attributes
===================

The attributes of the transcripted sentence.
See :ref:`reference/label_format:AttributesInformation` for details.

SentenceSubcatalog
==================

Before adding sentence labels to the dataset,
:class:`~tensorbay.label.label_sentence.SetenceSubcatalog` should be defined.

Besides :ref:`reference/label_format:AttributesInformation` in
:class:`~tensorbay.label.label_sentence.SetenceSubcatalog`,
it also has :attr:`~tensorbay.label.label_sentence.SetenceSubcatalog.is_sample`,
:attr:`~tensorbay.label.label_sentence.SetenceSubcatalog.sample_rate`
and :attr:`~tensorbay.label.label_sentence.SetenceSubcatalog.lexicon`.
to describe the transcripted sentences of the audio.

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
:class:`~tensorbay.label.label_sentence.SetenceSubcatalog`,
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
