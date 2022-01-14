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
    ... category="<LABEL_CATEGORY>",
    ... attributes={"<LABEL_ATTRIBUTE_NAME>": "<LABEL_ATTRIBUTE_VALUE>"},
    ... instance="<LABEL_INSTANCE_ID>"
    ... )
    >>> box3d_label
    LabeledBox3D(
      (size): Vector3D(10, 20, 30),
      (translation): Vector3D(0, 0, 0),
      (rotation): quaternion(1.0, 0.0, 0.0, 0.0),
      (category): '<LABEL_CATEGORY>',
      (attributes): {...},
      (instance): '<LABEL_INSTANCE_ID>'
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
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

Box3D.attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

Box3D.instance
==============

Instance is the unique id for the object inside of the 3D bounding box,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

Box3DSubcatalog
===============

Before adding the Box3D labels to data,
:class:`~tensorbay.label.label_box.Box3DSubcatalog` should be defined.

:class:`~tensorbay.label.label_box.Box3DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` and
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` for details.

The catalog with only Box3D subcatalog is typically stored in a json file as follows::

    {
        "BOX3D": {                                        <object>*
            "description":                                <string>! -- Subcatalog description, (default: "").
            "isTracking":                                <boolean>! -- Whether this type of label in the dataset contains tracking
                                                                       information, (default: false).
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

To add a :class:`~tensorbay.label.label_box.LabeledBox3D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("<DATA_LOCAL_PATH>")
    >>> data.label.box3d = []
    >>> data.label.box3d.append(box3d_label)

.. note::

   One data may contain multiple Box3D labels,
   so the :attr:`Data.label.box3d<tensorbay.dataset.data.Data.label.box3d>` must be a list.
