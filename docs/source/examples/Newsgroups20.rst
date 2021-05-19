###############
 20 Newsgroups
###############

This topic describes how to manage the `20 Newsgroups dataset`_, which is a dataset 
with :ref:`reference/label_format:Classification` label type.

.. _20 Newsgroups dataset: https://gas.graviti.cn/dataset/data-decorators/Newsgroups20

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************
  
.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************
  
It takes the following steps to organize the "20 Newsgroups" dataset by
the :class:`~tensorbay.dataset.dataset.Dataset` instance.

Step 1: Write the Catalog
=========================

A :ref:`Catalog <reference/dataset_structure:Catalog>` contains all label information of one dataset,
which is typically stored in a json file.

.. literalinclude:: ../../../tensorbay/opendataset/Newsgroups20/catalog.json
   :language: json
   :name: Newsgroups20-catalog
   :linenos:

The only annotation type for "20 Newsgroups" is :ref:`reference/label_format:Classification`,
and there are 20 :ref:`reference/label_format:Category` types.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different label types.

.. note::
   The :ref:`categories<reference/label_format:Category>` in
   :ref:`reference/dataset_structure:Dataset` "20 Newsgroups" have parent-child relationship,
   and it use "." to sparate different levels.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:Dataloader` is neeeded to organize the dataset into a
:class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../tensorbay/opendataset/Newsgroups20/loader.py
   :language: python
   :name: Newsgroups20-dataloader
   :linenos:

See :ref:`Classification annotation <reference/label_format:Classification>` for more details.

.. note::

   The data in "20 Newsgroups" do not have extensions
   so that a "txt" extension is added to the remote path of each data file
   to ensure the loaded dataset could function well on TensorBay.

.. note::

   Since the :ref:`20 Newsgroups dataloader <Newsgroups20-dataloader>` above is already included
   in TensorBay, so it uses relative import. However, use regular import should be used when
   writing a new dataloader.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Organize Dataset / regular import"""
   :end-at: from tensorbay.label import LabeledBox2D

There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, importing an available dataloader is also feasible.

.. literalinclude:: ../../../examples/Newsgroups20.py
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
Please see :ref:`features/visualization:Visualization` for more details.

****************
 Upload Dataset
****************

The organized "20 Newsgroups" dataset can be uploaded to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :ref:`features/version_control:Version Control` for more details.

**************
 Read Dataset
**************

Now "20 Newsgroups" dataset can be read from TensorBay.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "20 Newsgroups", there are four
:ref:`Segments <reference/dataset_structure:Segment>`: ``20news-18828``,
``20news-bydate-test`` and ``20news-bydate-train``, ``20_newsgroups``.
Get the segment names by listing them all.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / list segment names"""
   :end-before: """"""

Get a segment by passing the required segment name.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the 20news-18828 :ref:`reference/dataset_structure:Segment`, there is a sequence of :ref:`reference/dataset_structure:Data`,
which can be obtained by index.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Classification` annotations,
which can be obtained by index.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "20 Newsgroups" dataset, which is ``Classification``.
The information stored in :ref:`reference/label_format:Category` is
one of the category names in "categories" list of :ref:`catalog.json <Newsgroups20-catalog>`.
See :ref:`this page <reference/label_format:Classification>` for more details about the
structure of Classification.
   
****************
 Delete Dataset
****************

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
