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
    >>> panoptic_mask_label = PanopticMask(local_path="/panoptic_mask/mask_image.png")
    >>> panoptic_mask_label.all_category_ids = {1: 2, 2: 2}
    >>> panoptic_mask_label
    PanopticMask("/panoptic_mask/mask_image.png")(
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
    PanopticMask("/panoptic_mask/mask_image.png")(
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

To add a :class:`~tensorbay.label.label_mask.PanopticMask` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.panoptic_mask = panoptic_mask_label

.. note::

   One data can only have one PanopticMask label,
   See :attr:`Data.label.panoptic_mask<tensorbay.dataset.data.Data.label.panoptic_mask>` for details.
