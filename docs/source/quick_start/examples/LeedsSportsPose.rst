..
 Copyright 2021 Graviti. Licensed under MIT License.
 
###################
 Leeds Sports Pose
###################

This topic describes how to manage the `Leeds Sports Pose Dataset <https://gas.graviti.cn/dataset/data-decorators/LeedsSportsPose>`_,
which is a dataset with :doc:`/reference/label_format/Keypoints2D` label(:numref:`Fig. %s <example-leedssportspose>`).

.. _example-leedssportspose:

.. figure:: /images/example-Keypoints2D.png
   :scale: 80 %
   :align: center

   The preview of an image with labels from "Leeds Sports Pose".

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************

Normally, ``dataloader.py`` and ``catalog.json`` are required to organize the "Leeds Sports Pose" dataset into the :class:`~tensorbay.dataset.dataset.Dataset` instance.
In this example, they are stored in the same directory like::

    Leeds Sports Pose/
        catalog.json
        dataloader.py

Step 1: Write the Catalog
=========================

A :ref:`reference/dataset_structure:catalog` contains all label information of one dataset, which
is typically stored in a json file like ``catalog.json``.

.. literalinclude:: ../../../../tensorbay/opendataset/LeedsSportsPose/catalog.json
   :language: json
   :name: LeedsSportsPose-catalog
   :linenos:

The only annotation type for "Leeds Sports Pose" is :doc:`/reference/label_format/Keypoints2D`.

.. note::

   By passing the path of the ``catalog.json``, :func:`~tensorbay.dataset.dataset.DatasetBase.load_catalog` supports loading the catalog into dataset.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different label types.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:dataloader` is needed to organize the dataset into
a :class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../../tensorbay/opendataset/LeedsSportsPose/loader.py
   :language: python
   :name: LeedsSportsPose-dataloader
   :linenos:

See :doc:`Keipoints2D annotation </reference/label_format/Keypoints2D>` for more details.


There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, importing an available dataloader is also feasible.

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Organize dataset / import dataloader"""
   :end-before: """"""

.. note::

   Note that catalogs are automatically loaded in available dataloaders, users do not have to write them again.

.. important::

   See :ref:`dataloader table <reference/glossary:dataloader>` for dataloaders with different label types.

*******************
 Visualize Dataset
*******************

Optionally, the organized dataset can be visualized by **Pharos**, which is a TensorBay SDK plug-in.
This step can help users to check whether the dataset is correctly organized.
Please see :doc:`/features/visualization` for more details.

****************
 Upload Dataset
****************

The organized "BSTLD" dataset can be uploaded to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :doc:`/features/version_control/index` for more details.

**************
 Read Dataset
**************

Now "Leeds Sports Pose" dataset can be read from TensorBay.

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:dataset` "Leeds Sports Pose", there is one
:ref:`reference/dataset_structure:segment` named ``default``. Get it by passing the segment name or the index.

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the default :ref:`reference/dataset_structure:segment`, there is a sequence of :ref:`reference/dataset_structure:data`,
which can be obtained by index.

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:data`,
there is a sequence of :doc:`/reference/label_format/Keypoints2D` annotations,
which can be obtained by index.

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "Leeds Sports Pose" dataset, which is ``keypoints2d``. The information stored in ``x`` (``y``) is
the x (y) coordinate of one keypoint of one keypoints list. The information stored in ``v`` is
the visible status of one keypoint of one keypoints list. See :doc:`/reference/label_format/Keypoints2D`
label format for more details.

****************
 Delete Dataset
****************

.. literalinclude:: ../../../../docs/code/LeedsSportsPose.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
