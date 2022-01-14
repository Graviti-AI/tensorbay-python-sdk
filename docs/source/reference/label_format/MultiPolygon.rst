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
    ... category="<LABEL_CATEGORY>",
    ... attributes={"<LABEL_ATTRIBUTE_NAME>": "<LABEL_ATTRIBUTE_VALUE>"},
    ... instance="<LABEL_INSTANCE_ID>"
    ... )
    >>> multipolygon_label
    LabeledMultiPolygon [
      Polygon [...],
      Polygon [...]
    ](
      (category): '<LABEL_CATEGORY>',
      (attributes): {...},
      (instance): '<LABEL_INSTANCE_ID'
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
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

MultiPolygon.attributes
=======================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

MultiPolygon.instance
=====================

Instance is the unique id for the object inside of polygonal regions,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

MultiPolygonSubcatalog
======================

Before adding the MultiPolygon labels to data,
:class:`~tensorbay.label.label_polygon.MultiPolygonSubcatalog` should be defined.

:class:`~tensorbay.label.label_polygon.MultiPolygonSubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` and
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` for details.

The catalog with only MultiPolygon subcatalog is typically stored in a json file as follows::

    {
        "MULTI_POLYGON": {                                <object>*
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

To add a :class:`~tensorbay.label.label_polygon.LabeledMultiPolygon` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("<DATA_LOCAL_PATH>")
    >>> data.label.multi_polygon = []
    >>> data.label.multi_polygon.append(multipolygon_label)

.. note::

   One data may contain multiple MultiPolygon labels,
   so the :attr:`Data.label.multi_polygon<tensorbay.dataset.data.Data.label.multi_polygon>` must be a list.
