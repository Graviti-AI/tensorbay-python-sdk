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

The gray-scale value of the pixel corresponds to the category id of the ``categories`` within the :class:`~tensorbay.label.label_mask.SemanticMaskSubcatalog`.

Each data can only be assigned with one :class:`~tensorbay.label.label_mask.SemanticMask` label.

To create a :class:`~tensorbay.label.label_mask.SemanticMask` label:

    >>> from tensorbay.label import SemanticMask
    >>> semantic_mask_label = SemanticMask(local_path="/semantic_mask/mask_image.png")
    >>> semantic_mask_label
    SemanticMask("/semantic_mask/mask_image.png")()

SemanticMask.all_attributes
===========================

``all_attributes`` is a dictionary that stores attributes for each category. Each attribute is stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

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

:class:`~tensorbay.label.label_mask.SemanticMaskSubcatalog` has mask categories and attributes,
see :ref:`reference/label_format/CommonSubcatalogProperties:mask category information` and
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` for details.

To add a :class:`~tensorbay.label.label_mask.SemanticMask` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.semantic_mask = semantic_mask_label

.. note::

   One data can only have one SemanticMask label,
   See :attr:`Data.label.semantic_mask<tensorbay.dataset.data.Data.label.semantic_mask>` for details.
