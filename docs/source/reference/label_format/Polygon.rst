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
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

Polygon.attributes
==================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

Polygon.instance
================

Instance is the unique id for the object inside of the polygonal region,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

PolygonSubcatalog
=================

Before adding the Polygon labels to data,
:class:`~tensorbay.label.label_polygon.PolygonSubcatalog` should be defined.

:class:`~tensorbay.label.label_polygon.PolygonSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` and
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` for details.

The catalog with only Polygon subcatalog is typically stored in a json file as follows::

    {
        "POLYGON": {                                      <object>*
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

To add a :class:`~tensorbay.label.label_polygon.LabeledPolygon` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.polygon = []
    >>> data.label.polygon.append(polygon_label)

.. note::

   One data may contain multiple Polygon labels,
   so the :attr:`Data.label.polygon<tensorbay.dataset.data.Data.label.polygon>` must be a list.
