###########
 Neolix OD
###########

This topic describes how to manage the `Neolix OD dataset`_,
which is a dataset with :ref:`reference/label_format:Box3D` label type
(:numref:`Fig. %s <example-neolixod>`).

.. _Neolix OD dataset: https://gas.graviti.cn/dataset/graviti-open-dataset/NeolixOD

.. _example-neolixod:

.. figure:: ../images/example-Box3D.png
   :scale: 50 %
   :align: center

   The preview of a point cloud from "Neolix OD" with Box3D labels.

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************


.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************

It takes the following steps to organize "Neolix OD" dataset by the :class:`~tensorbay.dataset.dataset.Dataset` instance.

Step 1: Write the Catalog
=========================

A :ref:`Catalog <reference/dataset_structure:catalog>` contains all label information of one dataset,
which is typically stored in a json file.

.. literalinclude:: ../../../tensorbay/opendataset/NeolixOD/catalog.json
   :language: json
   :name: neolixod-catalog
   :linenos:

The only annotation type for "Neolix OD" is :ref:`reference/label_format:Box3D`, and there are 15
:ref:`reference/label_format:Category` types and 3 :ref:`reference/label_format:Attributes` types.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different label types.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:dataloader` is needed to organize the dataset into
a :class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../tensorbay/opendataset/NeolixOD/loader.py
   :language: python
   :name: neolixod-dataloader
   :linenos:

See :ref:`Box3D annotation <reference/label_format:Box3D>` for more details.

.. note::

   Since the :ref:`Neolix OD dataloader <neolixod-dataloader>` above is already included in TensorBay,
   so it uses relative import.
   However, the regular import should be used when writing a new dataloader.

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Organize Dataset / regular import"""
   :end-at: from tensorbay.label import LabeledBox3D

There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, importing an available dataloader is also feasible.

.. literalinclude:: ../../../docs/code/NeolixOD.py
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

The organized "Neolix OD" dataset can be uploaded to tensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :ref:`features/version_control:Version Control` for more details.

**************
 Read Dataset
**************

Now "Neolix OD" dataset can be read from TensorBay.

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "Neolix OD", there is only one default
:ref:`Segment <reference/dataset_structure:Segment>`: ``""`` (empty string).
Get a segment by passing the required segment name.

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the default :ref:`reference/dataset_structure:Segment`,
there is a sequence of :ref:`reference/dataset_structure:Data`,
which can be obtained by index.

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Box3D` annotations,

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "Neolix OD" dataset, which is ``box3d``.
The information stored in :ref:`reference/label_format:Category` is
one of the category names in "categories" list of :ref:`catalog.json <neolixod-catalog>`.
The information stored in :ref:`reference/label_format:Attributes`
is one of the attributes in "attributes" list of :ref:`catalog.json <neolixod-catalog>`.
See :ref:`reference/label_format:Box3D` label format for more details.

****************
 Delete Dataset
****************

.. literalinclude:: ../../../docs/code/NeolixOD.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
