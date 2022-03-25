..
 Copyright 2021 Graviti. Licensed under MIT License.
 
########
 BSTLD
########

This topic describes how to manage the `BSTLD Dataset <https://gas.graviti.cn/dataset/data-decorators/BSTLD>`_,
which is a dataset with :doc:`/reference/label_format/Box2D` label(:numref:`Fig. %s <example-bstld>`).

.. _example-bstld:

.. figure:: /images/example-Box2D.png
   :scale: 50 %
   :align: center

   The preview of a cropped image with labels from "BSTLD".

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************

Normally, ``dataloader.py`` and ``catalog.json`` are required to organize the "BSTLD" dataset into the :class:`~tensorbay.dataset.dataset.Dataset` instance.
In this example, they are stored in the same directory like::

    BSTLD/
        catalog.json
        dataloader.py

Step 1: Write the Catalog
=========================

A :ref:`reference/dataset_structure:catalog` contains all label information of one dataset, which
is typically stored in a json file like ``catalog.json``.

.. literalinclude:: ../../../../tensorbay/opendataset/BSTLD/catalog.json
   :language: json
   :name: BSTLD-catalog
   :linenos:

The only annotation type for "BSTLD" is :doc:`/reference/label_format/Box2D`, and there are 13
:ref:`reference/label_format/CommonLabelProperties:category` types and one :ref:`reference/label_format/CommonLabelProperties:attributes` type.

.. note::

   By passing the path of the ``catalog.json``, :func:`~tensorbay.dataset.dataset.DatasetBase.load_catalog` supports loading the catalog into dataset.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different label types.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:dataloader` is needed to organize the dataset into a :class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../../tensorbay/opendataset/BSTLD/loader.py
   :language: python
   :name: BSTLD-dataloader
   :linenos:

See :doc:`Box2D annotation </reference/label_format/Box2D>` for more details.

There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, in addition to writing, importing an available dataloader is also feasible.

.. literalinclude:: ../../../../docs/code/BSTLD.py
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

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

.. note::
   Set `skip_uploaded_files=True` to skip uploaded data.
   The data will be skiped if its name and segment name is the same as remote data.

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :doc:`/features/version_control/index` for more details.

**************
 Read Dataset
**************

Now "BSTLD" dataset can be read from TensorBay.

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:dataset` "BSTLD", there are three
:ref:`segments <reference/dataset_structure:segment>`: ``train``, ``test`` and ``additional``.
Get the segment names by listing them all.

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Read Dataset / list segment names"""
   :end-before: """"""

Get a segment by passing the required segment name.

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""


In the train :ref:`reference/dataset_structure:segment`, there is a sequence of :ref:`reference/dataset_structure:data`,
which can be obtained by index.

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:data`,
there is a sequence of :doc:`/reference/label_format/Box2D` annotations,
which can be obtained by index.

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "BSTLD" dataset, which is ``box2d``.
The information stored in :ref:`reference/label_format/CommonLabelProperties:category` is
one of the names in "categories" list of :ref:`catalog.json <BSTLD-catalog>`. The information stored
in :ref:`reference/label_format/CommonLabelProperties:attributes` is one or several of the attributes in "attributes" list of :ref:`catalog.json <BSTLD-catalog>`.
See :doc:`/reference/label_format/Box2D` label format for more details.

****************
 Delete Dataset
****************

.. literalinclude:: ../../../../docs/code/BSTLD.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
