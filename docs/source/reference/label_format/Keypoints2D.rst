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
:class:`~tensorbay.geometry.keypoint.Keypoints2D`.

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
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

Keypoints2D.attributes
======================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

Keypoints2D.instance
====================

Instance is the unique ID for the object inside of the 2D keypoints,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

Keypoints2DSubcatalog
=====================

Before adding 2D keypoints labels to the dataset,
:class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog` should be defined.

Besides :ref:`reference/label_format/CommonSubcatalogProperties:attributes information`,
:ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` in
:class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog`,
it also has :attr:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog.keypoints`
to describe a set of keypoints corresponding to certain categories.

The catalog with only Keypoints2D subcatalog is typically stored in a json file as follows::

    {
        "KEYPOINTS2D": {                                  <object>*
            "description":                                <string>! -- Subcatalog description, (default: "").
            "isTracking":                                <boolean>! -- Whether this type of label in the dataset contains tracking
                                                                       information, (default: false).
            "keypoints": [
                {
                    "number":                            <integer>* -- The number of key points.
                    "name":                                <array>  -- The name of each key point that corresponds to the
                                                                       "keypoints2d" in the Keypoints2D label via index.
                    "skeleton": [                          <array>  -- Key points skeleton for visualization.
                        [<index>, <index>],                <array>  -- Each array represents a line segment. The skeleton is formed
                                                                       by connecting these lines corresponding to the value of
                                                                       <index>.
                        ...
                    ],
                    "visible":                            <string>  -- Indicates the meaning of field "v" in the Keypoints2D label.
                                                                       There are two cases as follows:
                                                                       1. "TERNARY": v=0: invisible, v=1: occluded, v=2: visible.
                                                                       2. "BINARY": v=0: invisible, v=1: visible.
                                                                       Do not add this field if the field "v" does not exist.
                    "parentCategories": [...],             <array>  -- A list of categories indicating to which category the
                                                                       keypoints rule applies.Do not add this field if the keypoints
                                                                       rule applies to all the categories of the entire dataset.
                    "description":                        <string>! -- Key points description, (default: "").
                },
            ],
            "categoryDelimiter":                          <string>  -- The delimiter in category names indicating subcategories.
                                                                       Recommended delimiter is ".". There is no "categoryDelimiter"
                                                                       field by default which means the category is of one level.
            "categories": [                                <array>  -- Category list, which contains all category information.
                {
                    "name":                               <string>* -- Category name.
                    "description":                        <string>! -- Category description, (default: "").
                },
                ...
                ...
            ],
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
                    "parentCategories": [...],             <array>  -- Indicates the category to which the attribute belongs. Do not
                                                                       add this field if it is a global attribute.
                    "description":                        <string>! -- Attribute description, (default: "").
                },
                ...
                ...
            ]
        }
    }

.. note::

   ``*`` indicates that the field is required. ``!`` indicates that the field has a default value.

Besides giving the parameters while initializing
:class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog`,
it's also feasible to set them after initialization.

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

To add a :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.keypoints2d = []
    >>> data.label.keypoints2d.append(keypoints2d_label)

.. note::

   One data may contain multiple Keypoints2D labels,
   so the :attr:`Data.label.keypoints2d<tensorbay.dataset.data.Data.label.keypoints2d>`
   must be a list.
