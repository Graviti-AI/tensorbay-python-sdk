..
 Copyright 2021 Graviti. Licensed under MIT License.
 
###########
 Neolix OD
###########

This topic describes how to manage the `Neolix OD dataset`_,
which is a dataset with :doc:`/reference/label_format/Box3D` label type
(:numref:`Fig. %s <example-neolixod>`).

.. _Neolix OD dataset: https://gas.graviti.cn/dataset/graviti-open-dataset/NeolixOD

.. _example-neolixod:

.. figure:: /images/example-Box3D.png
   :scale: 50 %
   :align: center

   The preview of a point cloud from "Neolix OD" with Box3D labels.

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************


.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************

Normally, ``dataloader.py`` and ``catalog.json`` are required to organize the "Neolix OD" dataset into the :class:`~tensorbay.dataset.dataset.Dataset` instance.
In this example, they are stored in the same directory like::

    Neolix OD/
        catalog.json
        dataloader.py

Step 1: Write the Catalog
=========================

A :ref:`Catalog <reference/dataset_structure:catalog>` contains all label information of one dataset,
which is typically stored in a json file like ``catalog.json``.

.. literalinclude:: ../../../../tensorbay/opendataset/NeolixOD/catalog.json
   :language: json
   :name: neolixod-catalog
   :linenos:

The only annotation type for "Neolix OD" is :doc:`/reference/label_format/Box3D`, and there are 15
:ref:`reference/label_format/CommonLabelProperties:Category` types and 3 :ref:`reference/label_format/CommonLabelProperties:Attributes` types.

.. note::

   By passing the path of the ``catalog.json``, :func:`~tensorbay.dataset.dataset.DatasetBase.load_catalog` supports loading the catalog into dataset.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different label types.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:dataloader` is needed to organize the dataset into
a :class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../../tensorbay/opendataset/NeolixOD/loader.py
   :language: python
   :name: neolixod-dataloader
   :linenos:

See :doc:`Box3D annotation </reference/label_format/Box3D>` for more details.


There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, in addition to writing, importing an available dataloader is also feasible.

.. literalinclude:: ../../../../docs/code/NeolixOD.py
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

The organized "Neolix OD" dataset can be uploaded to tensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :doc:`/features/version_control/index` for more details.

**************
 Read Dataset
**************

Now "Neolix OD" dataset can be read from TensorBay.

.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "Neolix OD", there is only one
:ref:`segment <reference/dataset_structure:Segment>`: ``default``.
Get a segment by passing the required segment name or the index.

.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the default :ref:`reference/dataset_structure:Segment`,
there is a sequence of :ref:`reference/dataset_structure:Data`,
which can be obtained by index.

.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :doc:`/reference/label_format/Box3D` annotations,

.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "Neolix OD" dataset, which is ``box3d``.
The information stored in :ref:`reference/label_format/CommonLabelProperties:Category` is
one of the category names in "categories" list of :ref:`catalog.json <neolixod-catalog>`.
The information stored in :ref:`reference/label_format/CommonLabelProperties:Attributes`
is one of the attributes in "attributes" list of :ref:`catalog.json <neolixod-catalog>`.
See :doc:`/reference/label_format/Box3D` label format for more details.

****************
 Delete Dataset
****************

.. literalinclude:: ../../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
