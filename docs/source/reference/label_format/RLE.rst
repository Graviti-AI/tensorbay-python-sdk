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
    ... category="<LABEL_CATEGORY>",
    ... attributes={"<LABEL_ATTRIBUTE_NAME>": "<LABEL_ATTRIBUTE_VALUE>"},
    ... instance="<LABEL_INSTANCE_ID>"
    ... )
    >>> rle_label
    LabeledRLE [
      8,
      4,
      1,
      ...
    ](
      (category): '<LABEL_CATEGORY>',
      (attributes): {...},
      (instance): '<LABEL_INSTANCE_ID>'
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
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

RLE.attributes
==============

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

RLE.instance
============

Instance is the unique id for the object inside the region represented by rle format mask,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

RLESubcatalog
=============

Before adding the RLE labels to data,
:class:`~tensorbay.label.label_polygon.RLESubcatalog` should be defined.

:class:`~tensorbay.label.label_polygon.RLESubcatalog`
has categories, attributes and tracking information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` and
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` for details.

The catalog with only RLE subcatalog is typically stored in a json file as follows::

    {
        "RLE": {                                          <object>*
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

To add a :class:`~tensorbay.label.label_polygon.LabeledRLE` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("<DATA_LOCAL_PATH>")
    >>> data.label.rle = []
    >>> data.label.rle.append(rle_label)

.. note::

   One data may contain multiple RLE labels,
   so the :attr:`Data.label.rle<tensorbay.dataset.data.Data.label.rle>` must be a list.
