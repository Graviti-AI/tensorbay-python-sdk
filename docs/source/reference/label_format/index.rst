##############
 Label Format
##############

TensorBay supports multiple types of labels.

Each :class:`~tensorbay.dataset.data.Data` instance
can have multiple types of :class:`label <~tensorbay.label.label.Label>`.

And each type of :class:`label <~tensorbay.label.label.Label>` is supported with a specific label
class,
and has a corresponding :ref:`subcatalog <reference/dataset_structure:Catalog>` class.

.. table:: supported label types
   :widths: auto

   ============================================================= ===============================================================  =======================================================================
   supported label types                                         label classes                                                    subcatalog classes
   ============================================================= ===============================================================  =======================================================================
   :ref:`reference/label_format/Classification:Classification`   :class:`~tensorbay.label.label_classification.Classification`    :class:`~tensorbay.label.label_classification.ClassificationSubcatalog`
   :ref:`reference/label_format/Box2D:Box2D`                     :class:`~tensorbay.label.label_box.LabeledBox2D`                 :class:`~tensorbay.label.label_box.Box2DSubcatalog`
   :ref:`reference/label_format/Box3D:Box3D`                     :class:`~tensorbay.label.label_box.LabeledBox3D`                 :class:`~tensorbay.label.label_box.Box3DSubcatalog`
   :ref:`reference/label_format/Keypoints2D:Keypoints2D`         :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D`     :class:`~tensorbay.label.label_keypoints.Keypoints2DSubcatalog`
   :ref:`reference/label_format/Polygon:Polygon`                 :class:`~tensorbay.label.label_polygon.LabeledPolygon`           :class:`~tensorbay.label.label_polygon.PolygonSubcatalog`
   :ref:`reference/label_format/MultiPolygon:MultiPolygon`       :class:`~tensorbay.label.label_polygon.LabeledMultiPolygon`      :class:`~tensorbay.label.label_polygon.MultiPolygonSubcatalog`
   :ref:`reference/label_format/RLE:RLE`                         :class:`~tensorbay.label.label_polygon.LabeledRLE`               :class:`~tensorbay.label.label_polygon.RLESubcatalog`
   :ref:`reference/label_format/Polyline2D:Polyline2D`           :class:`~tensorbay.label.label_polyline.LabeledPolyline2D`       :class:`~tensorbay.label.label_polyline.Polyline2DSubcatalog`
   :ref:`reference/label_format/MultiPolyline2D:MultiPolyline2D` :class:`~tensorbay.label.label_polyline.LabeledMultiPolyline2D`  :class:`~tensorbay.label.label_polyline.MultiPolyline2DSubcatalog`
   :ref:`reference/label_format/Sentence:Sentence`               :class:`~tensorbay.label.label_sentence.LabeledSentence`         :class:`~tensorbay.label.label_sentence.SentenceSubcatalog`
   :ref:`reference/label_format/SemanticMask:SemanticMask`       :class:`~tensorbay.label.label_mask.SemanticMask`                :class:`~tensorbay.label.label_mask.SemanticMaskSubcatalog`
   :ref:`reference/label_format/InstanceMask:InstanceMask`       :class:`~tensorbay.label.label_mask.InstanceMask`                :class:`~tensorbay.label.label_mask.InstanceMaskSubcatalog`
   :ref:`reference/label_format/PanopticMask:PanopticMask`       :class:`~tensorbay.label.label_mask.PanopticMask`                :class:`~tensorbay.label.label_mask.PanopticMaskSubcatalog`
   ============================================================= ===============================================================  =======================================================================

.. toctree::
   :hidden:
   :maxdepth: 1

   CommonLabelProperties
   CommonSubcatalogProperties
   Classification
   Box2D
   Box3D
   Keypoints2D
   Polygon
   MultiPolygon
   RLE
   Polyline2D
   MultiPolyline2D
   Sentence
   SemanticMask
   InstanceMask
   PanopticMask
