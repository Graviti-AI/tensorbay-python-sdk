##############
 Label Format
##############

TensorBay supports multiple types of labels.

Each :class:`~tensorbay.dataset.data.Data` instance
can have multiple types of :class:`label <~tensorbay.label.basic.Label>`.

And each type of :class:`label <~tensorbay.label.basic.Label>` is supported with a specific label
class,
and has a corresponding :ref:`subcatalog <reference/dataset_structure:Catalog>` class.

.. table:: supported label types
   :widths: auto

   =============================================  ===============================================================  =======================================================================
   supported label types                          label classes                                                    subcatalog classes
   =============================================  ===============================================================  =======================================================================
   :ref:`reference/label_format:Classification`   :class:`~tensorbay.label.label_classification.Classification`    :class:`~tensorbay.label.label_classification.ClassificationSubcatalog`
   :ref:`reference/label_format:Box2D`            :class:`~tensorbay.label.label_box.LabeledBox2D`                 :class:`~tensorbay.label.label_box.Box2DSubcatalog`
   :ref:`reference/label_format:Box3D`            :class:`~tensorbay.label.label_box.LabeledBox3D`                 :class:`~tensorbay.label.label_box.Box3DSubcatalog`
   :ref:`reference/label_format:Keypoints2D`      :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D`     :class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog`
   :ref:`reference/label_format:Polygon`          :class:`~tensorbay.label.label_polygon.LabeledPolygon`           :class:`~tensorbay.label.label_polygon.PolygonSubcatalog`
   :ref:`reference/label_format:MultiPolygon`     :class:`~tensorbay.label.label_polygon.LabeledMultiPolygon`      :class:`~tensorbay.label.label_polygon.MultiPolygonSubcatalog`
   :ref:`reference/label_format:RLE`              :class:`~tensorbay.label.label_polygon.LabeledRLE`               :class:`~tensorbay.label.label_polygon.RLESubcatalog`
   :ref:`reference/label_format:Polyline2D`       :class:`~tensorbay.label.label_polyline.LabeledPolyline2D`       :class:`~tensorbay.label.label_polyline.Polyline2DSubcatalog`
   :ref:`reference/label_format:MultiPolyline2D`  :class:`~tensorbay.label.label_polyline.LabeledMultiPolyline2D`  :class:`~tensorbay.label.label_polyline.MultiPolyline2DSubcatalog`
   :ref:`reference/label_format:Sentence`         :class:`~tensorbay.label.label_sentence.LabeledSentence`         :class:`~tensorbay.label.label_sentence.SentenceSubcatalog`
   :ref:`reference/label_format:SemanticMask`     :class:`~tensorbay.label.label_mask.SemanticMask`                :class:`~tensorbay.label.label_mask.SemanticMaskSubcatalog`
   :ref:`reference/label_format:InstanceMask`     :class:`~tensorbay.label.label_mask.InstanceMask`                :class:`~tensorbay.label.label_mask.InstanceMaskSubcatalog`
   :ref:`reference/label_format:PanopticMask`     :class:`~tensorbay.label.label_mask.PanopticMask`                :class:`~tensorbay.label.label_mask.PanopticMaskSubcatalog`
   =============================================  ===============================================================  =======================================================================

*************************
 Common Label Properties
*************************

Different types of labels contain different aspects of annotation information about the data.
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

category
========

Category is a string indicating the class of the labeled object.

    >>> label.category
    'data_category'

attributes
==========

Attributes are the additional information about this data,
and there is no limit on the number of attributes.

The attribute names and values are stored in key-value pairs.

   >>> label.attributes
   {'attribute_name': 'attribute_value'}


instance
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

tracking information
====================

If the label of this type in the dataset has the information of instance IDs,
then the subcatalog should set a flag to show its support for tracking information.

Pass ``True`` to the ``is_tracking`` parameter while creating the subcatalog,
or set the ``is_tracking`` attr after initialization.

   >>> box2d_subcatalog.is_tracking = True

category information
====================

If the label of this type in the dataset has category,
then the subcatalog should contain all the optional categories.

Each :ref:`reference/label_format:category` of a label
appeared in the dataset should be within the categories of the subcatalog.

Category information can be added to the subcatalog.

    >>> box2d_subcatalog.add_category(name="cat", description="The Flerken")
    >>> box2d_subcatalog.categories
    NameList [
      CategoryInfo("cat")
    ]

:class:`~tensorbay.label.supports.CategoryInfo` is used to describe
a :ref:`reference/label_format:category`.
See details in :class:`~tensorbay.label.supports.CategoryInfo`.

attributes information
======================

If the label of this type in the dataset has attributes,
then the subcatalog should contain all the rules for different attributes.

Each :ref:`reference/label_format:attributes` of a label
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
    NameList [
      AttributeInfo("attribute_name")(...)
    ]

:class:`~tensorbay.label.attributes.AttributeInfo` is used to describe the rules of an
:ref:`reference/label_format:attributes`, which refers to the `Json schema`_ method.

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


Classification.category
=======================

The category of the entire data file.
See :ref:`reference/label_format:category` for details.

Classification.attributes
=========================

The attributes of the entire data file.
See :ref:`reference/label_format:attributes` for details.

.. note::

   There must be either a category or attributes in one classification label.

ClassificationSubcatalog
========================

Before adding the classification label to data,
:class:`~tensorbay.label.label_classification.ClassificationSubcatalog` should be defined.

:class:`~tensorbay.label.label_classification.ClassificationSubcatalog`
has categories and attributes information,
see :ref:`reference/label_format:category information` and
:ref:`reference/label_format:attributes information` for details.

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

Each data can be assigned with multiple Box2D labels.

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
    >>> LabeledBox2D.from_xywh(x=10, y=20, width=20, height=20)
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

Box2D.category
==============

The category of the object inside the 2D bounding box.
See :ref:`reference/label_format:category` for details.

Box2D.attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

Box2D.instance
==============

Instance is the unique ID for the object inside of the 2D bounding box,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

Box2DSubcatalog
===============

Before adding the Box2D labels to data,
:class:`~tensorbay.label.label_box.Box2DSubcatalog` should be defined.

:class:`~tensorbay.label.label_box.Box2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:category information`,
:ref:`reference/label_format:attributes information` and
:ref:`reference/label_format:tracking information` for details.

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

Box3D.category
==============

The category of the object inside the 3D bounding box.
See :ref:`reference/label_format:category` for details.

Box3D.attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

Box3D.instance
==============

Instance is the unique id for the object inside of the 3D bounding box,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

Box3DSubcatalog
===============

Before adding the Box3D labels to data,
:class:`~tensorbay.label.label_box.Box3DSubcatalog` should be defined.

:class:`~tensorbay.label.label_box.Box3DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:category information`,
:ref:`reference/label_format:attributes information` and
:ref:`reference/label_format:tracking information` for details.

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

Keypoints2D.category
====================

The category of the object inside the 2D keypoints.
See :ref:`reference/label_format:category` for details.

Keypoints2D.attributes
======================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

Keypoints2D.instance
====================

Instance is the unique ID for the object inside of the 2D keypoints,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

Keypoints2DSubcatalog
=====================

Before adding 2D keypoints labels to the dataset,
:class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog` should be defined.

Besides :ref:`reference/label_format:attributes information`,
:ref:`reference/label_format:category information`,
:ref:`reference/label_format:tracking information` in
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


*********
 Polygon
*********

Polygon is a type of label with a polygonal region on an image which contains some semantic information.
It's often used for CV tasks such as semantic segmentation.

Each data can be assigned with multiple Polygon labels.

The structure of one Polygon label is like::

    {
        "polygon": [
            {
                "x": <float>
                "y": <float>
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

To create a :class:`~tensorbay.label.label_polygon.LabeledPolygon` label:

    >>> from tensorbay.label import LabeledPolygon
    >>> polygon_label = LabeledPolygon(
    ... [(1, 2), (2, 3), (1, 3)],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> polygon_label
    LabeledPolygon [
      Vector2D(1, 2),
      Vector2D(2, 3),
      Vector2D(1, 3)
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )

Polygon.polygon
===============

:class:`~tensorbay.label.label_polygon.LabeledPolygon` extends :class:`~tensorbay.geometry.polygon.Polygon`.

To construct a :class:`~tensorbay.label.label_polygon.LabeledPolygon` instance with only the geometry
information, use the coordinates of the vertexes of the polygonal region.

    >>> LabeledPolygon([(1, 2), (2, 3), (1, 3)])
    LabeledPolygon [
      Vector2D(1, 2),
      Vector2D(2, 3),
      Vector2D(1, 3)
    ]()

It contains the basic geometry information of the polygonal region.

    >>> polygon_label.area()
    0.5

Polygon.category
================

The category of the object inside the polygonal region.
See :ref:`reference/label_format:category` for details.

Polygon.attributes
==================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

Polygon.instance
================

Instance is the unique id for the object inside of the polygonal region,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

PolygonSubcatalog
=================

Before adding the Polygon labels to data,
:class:`~tensorbay.label.label_polygon.PolygonSubcatalog` should be defined.

:class:`~tensorbay.label.label_polygon.PolygonSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:category information`,
:ref:`reference/label_format:attributes information` and
:ref:`reference/label_format:tracking information` for details.

To add a :class:`~tensorbay.label.label_polygon.LabeledPolygon` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.polygon = []
    >>> data.label.polygon.append(polygon_label)

.. note::

   One data may contain multiple Polygon labels,
   so the :attr:`Data.label.polygon<tensorbay.dataset.data.Data.label.polygon>` must be a list.

**************
 MultiPolygon
**************

MultiPolygon is a type of label with several polygonal regions which contain same semantic information on an image.
It's often used for CV tasks such as semantic segmentation.

Each data can be assigned with multiple MultiPolygon labels.

The structure of one MultiPolygon label is like::

    {
        "multiPolygon": [
            [
                {
                    "x": <float>
                    "y": <float>
                },
                ...
                ...
            ],
            ...
            ...
        ],
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        }
        "instance": <str>
    }

To create a :class:`~tensorbay.label.label_polygon.LabeledMultiPolygon` label:

    >>> from tensorbay.label import LabeledMultiPolygon
    >>> multipolygon_label = LabeledMultiPolygon(
    ... [[(1.0, 2.0), (2.0, 3.0), (1.0, 3.0)], [(1.0, 4.0), (2.0, 3.0), (1.0, 8.0)]],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> multipolygon_label
    LabeledMultiPolygon [
      Polygon [...],
      Polygon [...]
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )

MultiPolygon.multi_polygon
==========================

:class:`~tensorbay.label.label_polygon.LabeledMultiPolygon` extends :class:`~tensorbay.geometry.polygon.MultiPolygon`.

To construct a :class:`~tensorbay.label.label_polygon.LabeledMultiPolygon` instance with only the geometry
information, use the coordinates of the vertexes of polygonal regions.

    >>> LabeledMultiPolygon([[[1.0, 4.0], [2.0, 3.7], [7.0, 4.0]],
    ... [[5.0, 7.0], [6.0, 7.0], [9.0, 8.0]]])
    LabeledMultiPolygon [
      Polygon [...],
      Polygon [...]
    ]()

MultiPolygon.category
=====================

The category of the object inside polygonal regions.
See :ref:`reference/label_format:category` for details.

MultiPolygon.attributes
=======================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

MultiPolygon.instance
=====================

Instance is the unique id for the object inside of polygonal regions,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

MultiPolygonSubcatalog
======================

Before adding the MultiPolygon labels to data,
:class:`~tensorbay.label.label_polygon.MultiPolygonSubcatalog` should be defined.

:class:`~tensorbay.label.label_polygon.MultiPolygonSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:category information`,
:ref:`reference/label_format:attributes information` and
:ref:`reference/label_format:tracking information` for details.

To add a :class:`~tensorbay.label.label_polygon.LabeledMultiPolygon` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.multi_polygon = []
    >>> data.label.multi_polygon.append(multipolygon_label)

.. note::

   One data may contain multiple MultiPolygon labels,
   so the :attr:`Data.label.multi_polygon<tensorbay.dataset.data.Data.label.multi_polygon>` must be a list.

*****
 RLE
*****

RLE, Run-Length Encoding, is a type of label with a list of numbers to indicate whether the pixels are in
the target region. It's often used for CV tasks such as semantic segmentation.

Each data can be assigned with multiple RLE labels.

The structure of one RLE label is like::

    {
        "rle": [
            int,
            ...
        ]
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        }
        "instance": <str>
    }

To create a :class:`~tensorbay.label.label_polygon.LabeledRLE` label:

    >>> from tensorbay.label import LabeledRLE
    >>> rle_label = LabeledRLE(
    ... [8, 4, 1, 3, 12, 7, 16, 2, 9, 2],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> rle_label
    LabeledRLE [
      8,
      4,
      1,
      ...
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )

RLE.rle
=======

:class:`~tensorbay.label.label_polygon.LabeledRLE` extends :class:`~tensorbay.geometry.polygon.RLE`.

To construct a :class:`~tensorbay.label.label_polygon.LabeledRLE` instance with only the rle format mask.

    >>> LabeledRLE([8, 4, 1, 3, 12, 7, 16, 2, 9, 2])
    LabeledRLE [
      8,
      4,
      1,
      ...
    ]()

RLE.category
============

The category of the object inside the region represented by rle format mask.
See :ref:`reference/label_format:category` for details.

RLE.attributes
==============

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

RLE.instance
============

Instance is the unique id for the object inside the region represented by rle format mask,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

RLESubcatalog
=============

Before adding the RLE labels to data,
:class:`~tensorbay.label.label_polygon.RLESubcatalog` should be defined.

:class:`~tensorbay.label.label_polygon.RLESubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:category information`,
:ref:`reference/label_format:attributes information` and
:ref:`reference/label_format:tracking information` for details.

To add a :class:`~tensorbay.label.label_polygon.LabeledRLE` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.rle = []
    >>> data.label.rle.append(rle_label)

.. note::

   One data may contain multiple RLE labels,
   so the :attr:`Data.label.rle<tensorbay.dataset.data.Data.label.rle>` must be a list.

************
 Polyline2D
************

Polyline2D is a type of label with a 2D polyline on an image.
It's often used for CV tasks such as lane detection.

Each data can be assigned with multiple Polyline2D labels.

The structure of one Polyline2D label is like::

    {
        "polyline2d": [
            {
                "x": <float>
                "y": <float>
            },
            ...
            ...
        ],
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        }
        "instance": <str>
    }

To create a :class:`~tensorbay.label.label_polyline.LabeledPolyline2D` label:

    >>> from tensorbay.label import LabeledPolyline2D
    >>> polyline2d_label = LabeledPolyline2D(
    ... [(1, 2), (2, 3)],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> polyline2d_label
    LabeledPolyline2D [
      Vector2D(1, 2),
      Vector2D(2, 3)
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )

Polyline2D.polyline2d
=====================

:class:`~tensorbay.label.label_polyline.LabeledPolyline2D` extends :class:`~tensorbay.geometry.polyline.Polyline2D`.

To construct a :class:`~tensorbay.label.label_polyline.LabeledPolyline2D` instance with only the geometry
information, use the coordinates of the vertexes of the polyline.

    >>> LabeledPolyline2D([[1, 2], [2, 3]])
    LabeledPolyline2D [
      Vector2D(1, 2),
      Vector2D(2, 3)
    ]()


It contains a series of methods to operate on polyline.

    >>> polyline_1 = LabeledPolyline2D([[1, 1], [1, 2], [2, 2]])
    >>> polyline_2 = LabeledPolyline2D([[4, 5], [2, 1], [3, 3]])
    >>> LabeledPolyline2D.uniform_frechet_distance(polyline_1, polyline_2)
    3.6055512754639896
    >>> LabeledPolyline2D.similarity(polyline_1, polyline_2)
    0.2788897449072021


Polyline2D.category
===================

The category of the 2D polyline.
See :ref:`reference/label_format:category` for details.

Polyline2D.attributes
=====================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

Polyline2D.instance
===================

Instance is the unique ID for the 2D polyline,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

Polyline2DSubcatalog
====================

Before adding the Polyline2D labels to data,
:class:`~tensorbay.label.label_polyline.Polyline2DSubcatalog` should be defined.

:class:`~tensorbay.label.label_polyline.Polyline2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:category information`,
:ref:`reference/label_format:attributes information` and
:ref:`reference/label_format:tracking information` for details.

To add a :class:`~tensorbay.label.label_polyline.LabeledPolyline2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.polyline2d = []
    >>> data.label.polyline2d.append(polyline2d_label)

.. note::

   One data may contain multiple Polyline2D labels,
   so the :attr:`Data.label.polyline2d<tensorbay.dataset.data.Data.label.polyline2d>` must be a list.

*****************
 MultiPolyline2D
*****************

MultiPolyline2D is a type of label with several 2D polylines which belong to the same category on an image.
It's often used for CV tasks such as lane detection.

Each data can be assigned with multiple MultiPolyline2D labels.

The structure of one MultiPolyline2D label is like::

    {
        "multiPolyline2d": [
            [
                {
                    "x": <float>
                    "y": <float>
                },
                ...
                ...
            ],
            ...
            ...
        ],
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        }
        "instance": <str>
    }

To create a :class:`~tensorbay.label.label_polyline.LabeledMultiPolyline2D` label:

    >>> from tensorbay.label import LabeledMultiPolyline2D
    >>> multipolyline2d_label = LabeledMultiPolyline2D(
    ... [[[1, 2], [2, 3]], [[3, 4], [6, 8]]],
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> multipolyline2d_label
    LabeledMultiPolyline2D [
      Polyline2D [...],
      Polyline2D [...]
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )

MultiPolyline2D.multi_polyline2d
================================

:class:`~tensorbay.label.label_polyline.LabeledMultiPolyline2D` extends :class:`~tensorbay.geometry.polyline.MultiPolyline2D`.

To construct a :class:`~tensorbay.label.label_polyline.LabeledMultiPolyline2D` instance with only the geometry
information, use the coordinates of the vertexes of polylines.

    >>> LabeledMultiPolyline2D([[[1, 2], [2, 3]], [[3, 4], [6, 8]]])
    LabeledMultiPolyline2D [
      Polyline2D [...],
      Polyline2D [...]
    ]()


MultiPolyline2D.category
========================

The category of the multiple 2D polylines.
See :ref:`reference/label_format:category` for details.

MultiPolyline2D.attributes
==========================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

MultiPolyline2D.instance
========================

Instance is the unique ID for the multiple 2D polylines,
which is mostly used for tracking tasks.
See :ref:`reference/label_format:instance` for details.

MultiPolyline2DSubcatalog
=========================

Before adding the MultiPolyline2D labels to data,
:class:`~tensorbay.label.label_polyline.MultiPolyline2DSubcatalog` should be defined.

:class:`~tensorbay.label.label_polyline.MultiPolyline2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format:category information`,
:ref:`reference/label_format:attributes information` and
:ref:`reference/label_format:tracking information` for details.

To add a :class:`~tensorbay.label.label_polyline.LabeledMultiPolyline2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.multi_polyline2d = []
    >>> data.label.multi_polyline2d.append(multipolyline2d_label)

.. note::

   One data may contain multiple MultiPolyline2D labels,
   so the :attr:`Data.label.multi_polyline2d<tensorbay.dataset.data.Data.label.multi_polyline2d>` must be a list.


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
See :ref:`reference/label_format:attributes information` for details.

SentenceSubcatalog
==================

Before adding sentence labels to the dataset,
:class:`~tensorbay.label.label_sentence.SentenceSubcatalog` should be defined.

Besides :ref:`reference/label_format:attributes information` in
:class:`~tensorbay.label.label_sentence.SentenceSubcatalog`,
it also has :attr:`~tensorbay.label.label_sentence.SentenceSubcatalog.is_sample`,
:attr:`~tensorbay.label.label_sentence.SentenceSubcatalog.sample_rate`
and :attr:`~tensorbay.label.label_sentence.SentenceSubcatalog.lexicon`.
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


**************
 SemanticMask
**************

SemanticMask is a type of label which is usually used for semantic segmentation task.

In TensorBay, the structure of SemanticMask label is unified as follows::

    {
        "localPath": <str>
        "info": [
            {
                "categoryId": <int>
                "attributes": {
                    <key>: <value>
                    ...
                    ...
                }
            },
            ...
            ...
        ]
    }

``local_path`` is the storage path of the mask image. TensorBay only supports single-channel, gray-scale png images.
If the number of categories exceeds 256, the color depth of this image should be 16 bits, otherwise it is 8 bits.

The gray-scale value of the pixel corresponds to the index of the ``categories`` within the :class:`~tensorbay.label.label_mask.SemanticMaskSubcatalog`.

Each data can only be assigned with one :class:`~tensorbay.label.label_mask.SemanticMask` label.

To create a :class:`~tensorbay.label.label_mask.SemanticMask` label:

    >>> from tensorbay.label import SemanticMask
    >>> semantic_mask_label = SemanticMask(local_path="/semantic_mask/mask_image.png")
    >>> semantic_mask_label
    SemanticMask("/semantic_mask/mask_image.png")()

SemanticMask.all_attributes
===========================

``all_attributes`` is a dictionary that stores attributes for each category. Each attribute is stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

To create `all_attributes`:

    >>> semantic_mask_label.all_attributes = {1: {"occluded": True}, 2: {"occluded": False}}
    >>> semantic_mask_label
    SemanticMask("/semantic_mask/mask_image.png")(
      (all_attributes): {
        1: {
          'occluded': True
        },
        2: {
          'occluded': False
        }
      }
    )

.. note::

   In :class:`~tensorbay.label.label_mask.SemanticMask`, the key of `all_attributes` is category id which should be an integer.

SemanticMaskSubcatalog
======================

Before adding the SemanticMask labels to data,
:class:`~tensorbay.label.label_mask.SemanticMaskSubcatalog` should be defined.

:class:`~tensorbay.label.label_mask.SemanticMaskSubcatalog` has categories and attributes,
see :ref:`reference/label_format:category information` and
:ref:`reference/label_format:attributes information` for details.

To add a :class:`~tensorbay.label.label_mask.SemanticMask` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.semantic_mask = semantic_mask_label

.. note::

   One data can only have one SemanticMask label,
   See :attr:`Data.label.semantic_mask<tensorbay.dataset.data.Data.label.semantic_mask>` for details.

**************
 InstanceMask
**************

InstanceMask is a type of label which is usually used for semantic segmentation task.

In TensorBay, the structure of InstanceMask label is unified as follows::

    {
        "localPath": <str>
        "info": [
            {
                "instanceId": <int>
                "attributes": {
                    <key>: <value>
                    ...
                    ...
                }
            },
            ...
            ...
        ]
    }

``local_path`` is the storage path of the mask image. TensorBay only supports single-channel, gray-scale png images.
If the number of categories exceeds 256, the color depth of this image should be 16 bits, otherwise it is 8 bits.

Each data can only be assigned with one :class:`~tensorbay.label.label_mask.InstanceMask` label.

To create a :class:`~tensorbay.label.label_mask.InstanceMask` label:

    >>> from tensorbay.label import InstanceMask
    >>> instance_mask_label = InstanceMask(local_path="/instance_mask/mask_image.png")
    >>> instance_mask_label
    InstanceMask("/instance_mask/mask_image.png")()

InstanceMask.all_attributes
===========================

`all_attributes` is a dictionary that stores attributes for each instance. Each attribute is stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

To create `all_attributes`:

    >>> instance_mask_label.all_attributes = {1: {"occluded": True}, 2: {"occluded": True}}
    >>> instance_mask_label
    InstanceMask("/instance_mask/mask_image.png")(
      (all_attributes): {
        1: {
          'occluded': True
        },
        2: {
          'occluded': True
        }
      }
    )

.. note::

   In :class:`~tensorbay.label.label_mask.InstanceMask`, the key of `all_attributes` is instance id which should be an integer.

InstanceMaskSubcatalog
======================

Before adding the InstanceMask labels to data,
:class:`~tensorbay.label.label_mask.InstanceMaskSubcatalog` should be defined.

:class:`~tensorbay.label.label_mask.InstanceMaskSubcatalog` has attributes,
see :ref:`reference/label_format:attributes information` for details.

To add a :class:`~tensorbay.label.label_mask.InstanceMask` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.instance_mask = instance_mask_label

.. note::

   One data can only have one InstanceMask label,
   See :attr:`Data.label.instance_mask<tensorbay.dataset.data.Data.label.instance_mask>` for details.

**************
 PanopticMask
**************

PanopticMask is a type of label which is usually used for panoptic segmentation task.

In TensorBay, the structure of PanopticMask label is unified as follows::

    {
        "localPath": <str>
        "info": [
            {
                "instanceId": <int>
                "categoryId": <int>
                "attributes": {
                    <key>: <value>
                    ...
                    ...
                }
            }
            ...
            ...
        ],
    }

``local_path`` is the storage path of the mask image. TensorBay only supports single-channel, gray-scale png images.
If the number of categories exceeds 256, the color depth of this image should be 16 bits, otherwise it is 8 bits.

The gray-scale value of the pixel corresponds to the index of the ``categories`` within the :class:`~tensorbay.label.label_mask.PanopticMaskSubcatalog`.

Each data can only be assigned with one :class:`~tensorbay.label.label_mask.PanopticMask` label.

To create a :class:`~tensorbay.label.label_mask.PanopticMask` label:

    >>> from tensorbay.label import PanopticMask
    >>> panoptic_mask_label = PanopticMask(local_path="/panoptic_mask/mask_image.png")
    >>> panoptic_mask_label.all_category_ids = {1: 2, 2: 2}
    >>> panoptic_mask_label
    PanopticMask("/panoptic_mask/mask_image.png")(
      (all_category_ids): {
        1: 2,
        2: 2
      }
    )

.. note::

   In :class:`~tensorbay.label.label_mask.PanopticMask`, the key and value of `all_category_ids` are instance id and category id, respectively, which both should be integers.

PanopticMask.all_attributes
===========================

`all_attributes` is a dictionary that stores attributes for each instance. Each attribute is stored in key-value pairs.
See :ref:`reference/label_format:attributes` for details.

To create `all_attributes`:

    >>> panoptic_mask_label.all_attributes = {1: {"occluded": True}, 2: {"occluded": True}}
    >>> panoptic_mask_label
    PanopticMask("/panoptic_mask/mask_image.png")(
      (all_category_ids): {
        1: 2,
        2: 2
      },
      (all_attributes): {
        1: {
          'occluded': True
        },
        2: {
          'occluded': True
        }
      }
    )

.. note::

   In :class:`~tensorbay.label.label_mask.PanopticMask`, the key of `all_attributes` is instance id which should be integer.

PanopticMaskSubcatalog
======================

Before adding the PanopticMask labels to data,
:class:`~tensorbay.label.label_mask.PanopticMaskSubcatalog` should be defined.

:class:`~tensorbay.label.label_mask.PanopticMaskSubcatalog` has categories and attributes,
see :ref:`reference/label_format:category information` and
:ref:`reference/label_format:attributes information` for details.

To add a :class:`~tensorbay.label.label_mask.PanopticMask` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.panoptic_mask = panoptic_mask_label

.. note::

   One data can only have one PanopticMask label,
   See :attr:`Data.label.panoptic_mask<tensorbay.dataset.data.Data.label.panoptic_mask>` for details.
