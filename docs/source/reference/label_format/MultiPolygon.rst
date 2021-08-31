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
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> multipolygon_label
    LabeledMultiPolygon [
      Polygon [...],
      Polygon [...]
    ](
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
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

To add a :class:`~tensorbay.label.label_polygon.LabeledMultiPolygon` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.multi_polygon = []
    >>> data.label.multi_polygon.append(multipolygon_label)

.. note::

   One data may contain multiple MultiPolygon labels,
   so the :attr:`Data.label.multi_polygon<tensorbay.dataset.data.Data.label.multi_polygon>` must be a list.
