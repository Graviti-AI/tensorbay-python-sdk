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

To add a :class:`~tensorbay.label.label_polygon.LabeledPolygon` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.polygon = []
    >>> data.label.polygon.append(polygon_label)

.. note::

   One data may contain multiple Polygon labels,
   so the :attr:`Data.label.polygon<tensorbay.dataset.data.Data.label.polygon>` must be a list.
