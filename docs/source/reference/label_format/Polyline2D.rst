************
 Polyline2D
************

Polyline2D is a type of label with a 2D polyline on an image.
It's often used for CV tasks such as lane detection.

Each data can be assigned with multiple Polyline2D labels.

The structure of one Polyline2D label is like::

    {
        "polyline2d": [
            {
                "x": <float>
                "y": <float>
            },
            ...
            ...
        ],
        "beizerPointTypes": <str>
        "category": <str>
        "attributes": {
            <key>: <value>
            ...
            ...
        }
        "instance": <str>
    }

.. note::

   When the ``is_beizer_curve`` is ``True`` in the :ref:`reference/label_format/Polyline2D:Polyline2DSubcatalog`, ``beizerPointTypes`` is mandatory,
   where each character in the string represents the type of the point ("L" represents the vertex and "C" represents the control point) at the corresponding position in the ``polyline2d`` list.

To create a :class:`~tensorbay.label.label_polyline.LabeledPolyline2D` label:

    >>> from tensorbay.label import LabeledPolyline2D
    >>> polyline2d_label = LabeledPolyline2D(
    ... [(1, 2), (2, 3)],
    ... beizer_point_types="LL",
    ... category="category",
    ... attributes={"attribute_name": "attribute_value"},
    ... instance="instance_ID"
    ... )
    >>> polyline2d_label
    LabeledPolyline2D [
      Vector2D(1, 2),
      Vector2D(2, 3)
    ](
      (beizer_point_types): 'LL',
      (category): 'category',
      (attributes): {...},
      (instance): 'instance_ID'
    )


Polyline2D.polyline2d
=====================

:class:`~tensorbay.label.label_polyline.LabeledPolyline2D` extends :class:`~tensorbay.geometry.polyline.Polyline2D`.

To construct a :class:`~tensorbay.label.label_polyline.LabeledPolyline2D` instance with only the geometry
information, use the coordinates of the vertexes of the polyline.

    >>> LabeledPolyline2D([[1, 2], [2, 3]])
    LabeledPolyline2D [
      Vector2D(1, 2),
      Vector2D(2, 3)
    ]()


It contains a series of methods to operate on polyline.

    >>> polyline_1 = LabeledPolyline2D([[1, 1], [1, 2], [2, 2]])
    >>> polyline_2 = LabeledPolyline2D([[4, 5], [2, 1], [3, 3]])
    >>> LabeledPolyline2D.uniform_frechet_distance(polyline_1, polyline_2)
    3.6055512754639896
    >>> LabeledPolyline2D.similarity(polyline_1, polyline_2)
    0.2788897449072021


Polyline2D.category
===================

The category of the 2D polyline.
See :ref:`reference/label_format/CommonLabelProperties:category` for details.

Polyline2D.attributes
=====================

Attributes are the additional information about this object, which are stored in key-value pairs.
See :ref:`reference/label_format/CommonLabelProperties:attributes` for details.

Polyline2D.instance
===================

Instance is the unique ID for the 2D polyline,
which is mostly used for tracking tasks.
See :ref:`reference/label_format/CommonLabelProperties:instance` for details.

Polyline2DSubcatalog
====================

Before adding the Polyline2D labels to data,
:class:`~tensorbay.label.label_polyline.Polyline2DSubcatalog` should be defined.

Besides :ref:`reference/label_format/CommonSubcatalogProperties:common category information`,
:ref:`reference/label_format/CommonSubcatalogProperties:attributes information` and
:ref:`reference/label_format/CommonSubcatalogProperties:tracking information` in
:class:`~tensorbay.label.label_polyline.Polyline2DSubcatalog`,
it also has :attr:`~tensorbay.label.label_polyline.Polyline2DSubcatalog.is_beizer_curve`
to describe the type of the polyline.


   >>> from tensorbay.label import Polyline2DSubcatalog
   >>> polyline2d_subcatalog = Polyline2DSubcatalog(
   ... is_beizer_curve=True
   ... )
   >>> polyline2d_subcatalog
   Polyline2DSubcatalog(
     (is_beizer_curve): True,
     (is_tracking): False
   )

The ``is_beizer_curve`` is a boolen value indicating whether the polyline is a Bezier curve.

Besides giving the parameters while initializing
:class:`~tensorbay.label.label_sentence.Polyline2DSubcatalog`,
it's also feasible to set them after initialization.

   >>> from tensorbay.label import Polyline2DSubcatalog
   >>> polyline2d_subcatalog = Polyline2DSubcatalog()
   >>> polyline2d_subcatalog.is_beizer_curve = True
   >>> polyline2d_subcatalog
   Polyline2DSubcatalog(
     (is_beizer_curve): True,
     (is_tracking): False
   )

To add a :class:`~tensorbay.label.label_polyline.LabeledPolyline2D` label to one data:

    >>> from tensorbay.dataset import Data
    >>> data = Data("local_path")
    >>> data.label.polyline2d = []
    >>> data.label.polyline2d.append(polyline2d_label)

.. note::

   One data may contain multiple Polyline2D labels,
   so the :attr:`Data.label.polyline2d<tensorbay.dataset.data.Data.label.polyline2d>` must be a list.
