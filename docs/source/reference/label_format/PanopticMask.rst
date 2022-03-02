..
 Copyright 2021 Graviti. Licensed under MIT License.
 
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

The gray-scale value of the pixel corresponds to the category id of the ``categories`` within the :class:`~tensorbay.label.label_mask.PanopticMaskSubcatalog`.

Each data can only be assigned with one :class:`~tensorbay.label.label_mask.PanopticMask` label.

To create a :class:`~tensorbay.label.label_mask.PanopticMask` label:

    >>> from tensorbay.label import PanopticMask
    >>> panoptic_mask_label = PanopticMask(local_path="</panoptic_mask/mask_image.png>")
    >>> panoptic_mask_label.all_category_ids = {1: 2, 2: 2}
    >>> panoptic_mask_label
    PanopticMask("</panoptic_mask/mask_image.png>")(
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
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

To create `all_attributes`:

    >>> panoptic_mask_label.all_attributes = {1: {"occluded": True}, 2: {"occluded": True}}
    >>> panoptic_mask_label
    PanopticMask("</panoptic_mask/mask_image.png>")(
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

:class:`~tensorbay.label.label_mask.PanopticMaskSubcatalog` has mask categories and attributes,
see :ref:`reference/label_format/CommonSubcatalogProperties:mask category information` and
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` for details.

The catalog with only PanopticMask subcatalog is typically stored in a json file as follows::

    {
        "PANOPTIC_MASK": {                                <object>*
            "description":                                <string>! -- Subcatalog description, (default: "").
            "categoryDelimiter":                          <string>  -- The delimiter in category names indicating subcategories.
                                                                       Recommended delimiter is ".". There is no "categoryDelimiter"
                                                                       field by default which means the category is of one level.
            "categories": [                                <array>* -- Category list, which contains all category information.
                {
                    "name":                               <string>* -- Category name.
                    "categoryId":                        <integer>* -- Category id.
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

To add a :class:`~tensorbay.label.label_mask.PanopticMask` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("<DATA_LOCAL_PATH>")
    >>> data.label.panoptic_mask = panoptic_mask_label

.. note::

   One data can only have one PanopticMask label,
   See :attr:`Data.label.panoptic_mask<tensorbay.dataset.data.Data.label.panoptic_mask>` for details.
