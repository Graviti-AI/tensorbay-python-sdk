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
    ... category="<LABEL_CATEGORY>",
    ... attributes={"<LABEL_ATTRIBUTE_NAME>": "<LABEL_ATTRIBUTE_VALUE>"}
    ... )
    >>> classification_label
    Classification(
      (category): '<LABEL_CATEGORY>',
      (attributes): {...}
    )


Classification.category
=======================

The category of the entire data file.
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

Classification.attributes
=========================

The attributes of the entire data file.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

.. note::

   There must be either a category or attributes in one classification label.

ClassificationSubcatalog
========================

Before adding the classification label to data,
:class:`~tensorbay.label.label_classification.ClassificationSubcatalog` should be defined.

:class:`~tensorbay.label.label_classification.ClassificationSubcatalog`
has categories and attributes information,
see :ref:`reference/label_format/CommonSubcatalogProperties:common category information` and
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` for details.

The catalog with only Classification subcatalog is typically stored in a json file as follows::

    {
        "CLASSIFICATION": {                               <object>*
            "description":                                <string>! -- Subcatalog description, (default: "").
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

To add a :class:`~tensorbay.label.label_classification.Classification` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("<DATA_LOCAL_PATH>")
    >>> data.label.classification = classification_label

.. note::

   One data can only have one classification label.

