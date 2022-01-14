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
    ... category="<LABEL_CATEGORY>",
    ... attributes={"<LABEL_ATTRIBUTE_NAME>": "<LABEL_ATTRIBUTE_VALUE>"},
    ... instance="<LABEL_INSTANCE_ID>"
    ... )
    >>> box2d_label
    LabeledBox2D(xmin, ymin, xmax, ymax)(
      (category): '<LABEL_CATEGORY>',
      (attributes): {...}
      (instance): '<LABEL_INSTANCE_ID>'
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
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

Box2D.attributes
================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

Box2D.instance
==============

Instance is the unique ID for the object inside of the 2D bounding box,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

Box2DSubcatalog
===============

Before adding the Box2D labels to data,
:class:`~tensorbay.label.label_box.Box2DSubcatalog` should be defined.

:class:`~tensorbay.label.label_box.Box2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` and
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` for details.


The catalog with only Box2D subcatalog is typically stored in a json file as follows::

    {
        "BOX2D": {                                        <object>*
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

To add a :class:`~tensorbay.label.label_box.LabeledBox2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("<DATA_LOCAL_PATH>")
    >>> data.label.box2d = []
    >>> data.label.box2d.append(box2d_label)

.. note::

   One data may contain multiple Box2D labels,
   so the :attr:`Data.label.box2d<tensorbay.dataset.data.Data.label.box2d>` must be a list.
