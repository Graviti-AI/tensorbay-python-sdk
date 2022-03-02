..
 Copyright 2021 Graviti. Licensed under MIT License.
 
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
    ... category="<LABEL_CATEGORY>",
    ... attributes={"<LABEL_ATTRIBUTE_NAME>": "<LABEL_ATTRIBUTE_VALUE>"},
    ... instance="<LABEL_INSTANCE_ID>"
    ... )
    >>> multipolyline2d_label
    LabeledMultiPolyline2D [
      Polyline2D [...],
      Polyline2D [...]
    ](
      (category): '<LABEL_CATEGORY>',
      (attributes): {...},
      (instance): '<LABEL_INSTANCE_ID>'
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
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

MultiPolyline2D.attributes
==========================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

MultiPolyline2D.instance
========================

Instance is the unique ID for the multiple 2D polylines,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

MultiPolyline2DSubcatalog
=========================

Before adding the MultiPolyline2D labels to data,
:class:`~tensorbay.label.label_polyline.MultiPolyline2DSubcatalog` should be defined.

:class:`~tensorbay.label.label_polyline.MultiPolyline2DSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` and
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` for details.

The catalog with only MultiPolyline2D subcatalog is typically stored in a json file as follows::

    {
        "MULTI_POLYLINE2D": {                             <object>*
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

To add a :class:`~tensorbay.label.label_polyline.LabeledMultiPolyline2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("<DATA_LOCAL_PATH>")
    >>> data.label.multi_polyline2d = []
    >>> data.label.multi_polyline2d.append(multipolyline2d_label)

.. note::

   One data may contain multiple MultiPolyline2D labels,
   so the :attr:`Data.label.multi_polyline2d<tensorbay.dataset.data.Data.label.multi_polyline2d>` must be a list.
