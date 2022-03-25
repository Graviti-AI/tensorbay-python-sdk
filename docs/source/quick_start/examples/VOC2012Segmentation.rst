..
 Copyright 2021 Graviti. Licensed under MIT License.
 
######################
 VOC2012 Segmentation
######################

This topic describes how to manage the `VOC2012 Segmentation dataset`_,
which is a dataset with :doc:`/reference/label_format/SemanticMask`
and :doc:`/reference/label_format/InstanceMask` labels
(:numref:`Fig. %s <example-semantic-mask>` and :numref:`Fig. %s <example-instance-mask>`).

.. _VOC2012 Segmentation dataset: https://gas.graviti.cn/dataset/hello-dataset/VOC2012Segmentation

.. _example-semantic-mask:

.. figure:: /images/example-semanticmask.png
   :scale: 150 %
   :align: center

   The preview of a semantic mask from "VOC2012 Segmentation".

.. _example-instance-mask:

.. figure:: /images/example-instancemask.png
   :scale: 150 %
   :align: center

   The preview of a instance mask from "VOC2012 Segmentation".


*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************


.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************

Normally, ``dataloader.py`` and ``catalog.json`` are required to organize the "VOC2012 Segmentation" dataset into the :class:`~tensorbay.dataset.dataset.Dataset` instance.
In this example, they are stored in the same directory like::

    VOC2012 Segmentation/
        catalog.json
        dataloader.py


It takes the following steps to organize "VOC2012 Segmentation" dataset by the :class:`~tensorbay.dataset.dataset.Dataset` instance.

Step 1: Write the Catalog
=========================

A :ref:`Catalog <reference/dataset_structure:catalog>` contains all label information of one dataset,
which is typically stored in a json file like ``catalog.json``.

.. literalinclude:: ../../../../tensorbay/opendataset/VOC2012Segmentation/catalog.json
   :language: json
   :name: voc2012segmentation-catalog
   :linenos:

The annotation types for "VOC2012 Segmentation" are :doc:`/reference/label_format/SemanticMask`
and :doc:`/reference/label_format/InstanceMask`, and there are 22
:ref:`reference/label_format/CommonLabelProperties:Category` types for :doc:`/reference/label_format/SemanticMask`. There are 2
:ref:`reference/label_format/CommonLabelProperties:Category` types for :doc:`/reference/label_format/InstanceMask`, category 0 represents the
background, and category 255 represents the border of instances.

.. note::

   * By passing the path of the ``catalog.json``, :func:`~tensorbay.dataset.dataset.DatasetBase.load_catalog` supports loading the catalog into dataset.
   * The categories in :ref:`reference/label_format/InstanceMask:InstanceMaskSubcatalog` are for pixel values which are not instance ids.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different label types.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:dataloader` is needed to organize the dataset into
a :class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../../tensorbay/opendataset/VOC2012Segmentation/loader.py
   :language: python
   :name: voc2012segmentation-dataloader
   :linenos:

See :doc:`SemanticMask annotation </reference/label_format/SemanticMask>`
and :doc:`InstanceMask annotation </reference/label_format/InstanceMask>` for more details.


There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, in addition to writing, importing an available dataloader is also feasible.

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Organize dataset / import dataloader"""
   :end-before: """"""

.. note::

   Note that catalogs are automatically loaded in available dataloaders, users do not have to write them again.

.. important::

   See :ref:`dataloader table <reference/glossary:dataloader>` for dataloaders with different label types.

****************
 Upload Dataset
****************

The organized "VOC2012 Segmentation" dataset can be uploaded to tensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :doc:`/features/version_control/index` for more details.

See the visualization on TensorBay website.

**************
 Read Dataset
**************

Now "VOC2012 Segmentation" dataset can be read from TensorBay.

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "VOC2012 Segmentation", there are two
:ref:`segments <reference/dataset_structure:Segment>`: ``train`` and ``val``.
Get a segment by passing the required segment name or the index.

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the ``train`` :ref:`reference/dataset_structure:Segment`,
there is a sequence of :ref:`reference/dataset_structure:Data`,
which can be obtained by index.

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:Data`,
there are one :doc:`/reference/label_format/SemanticMask` annotation and one :doc:`/reference/label_format/InstanceMask` annotation.

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There are two label types in "VOC2012 Segmentation" dataset, which are ``semantic_mask`` and ``instance_mask``. We can
get the mask by ``Image.open()`` or get the mask url by ``get_url()``.
The information stored in :ref:`reference/label_format/SemanticMask:SemanticMask.all_attributes` is
attributes for every category in ``categories`` list of ``SEMANTIC_MASK``.
The information stored in :ref:`reference/label_format/InstanceMask:InstanceMask.all_attributes`
is attributes for every instance.
See :doc:`/reference/label_format/SemanticMask` and :doc:`/reference/label_format/InstanceMask` label formats for more details.

****************
 Delete Dataset
****************

.. literalinclude:: ../../../../docs/code/VOC2012Segmentation.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
