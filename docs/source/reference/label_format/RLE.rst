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
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> rle_label
    LabeledRLE [
      8,
      4,
      1,
      ...
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
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

To add a :class:`~tensorbay.label.label_polygon.LabeledRLE` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.rle = []
    >>> data.label.rle.append(rle_label)

.. note::

   One data may contain multiple RLE labels,
   so the :attr:`Data.label.rle<tensorbay.dataset.data.Data.label.rle>` must be a list.
