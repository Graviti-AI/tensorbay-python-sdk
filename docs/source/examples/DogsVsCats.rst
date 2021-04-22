##############
 Dogs vs Cats
##############

This topic describes how to manage the `Dogs vs Cats Dataset <https://gas.graviti.cn/dataset/data-decorators/DogsVsCats>`_,
which is a dataset with :ref:`reference/label_format:Classification` label.

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************

It takes the following steps to organize the "Dogs vs Cats" dataset by the :class:`~tensorbay.dataset.dataset.Dataset` instance.

Step 1: Write the Catalog
=========================

A :ref:`reference/dataset_structure:catalog` contains all label information of one dataset, which
is typically stored in a json file.

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/catalog.json
   :language: json
   :name: dogsvscats-catalog
   :linenos:

The only annotation type for "Dogs vs Cats" is :ref:`reference/label_format:Classification`, and there are 2
:ref:`reference/label_format:category` types.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different label types.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:dataloader` is needed to organize the dataset into
a :class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/loader.py
   :language: python
   :name: dogsvscats-dataloader
   :linenos:

See :ref:`Classification annotation <reference/label_format:Classification>` for more details.

.. note::

   Since the :ref:`Dogs vs Cats dataloader <dogsvscats-dataloader>` above is already included in TensorBay,
   so it uses relative import.
   However, the regular import should be used when writing a new dataloader.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Organize Dataset / regular import"""
   :end-at: from tensorbay.label import Classification

There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, importing an available dataloadert is also feasible.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Organize dataset / import dataloader"""
   :end-before: """"""

.. note::

   Note that catalogs are automatically loaded in available dataloaders, users do not have to write them again.

.. important::

   See :ref:`dataloader table <reference/glossary:dataloader>` for more examples of dataloaders with different label types.

****************
 Upload Dataset
****************

The organized "Dogs vs Cats" dataset can be uploaded to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :ref:`features/version_control:Version Control` for more details.

**************
 Read Dataset
**************

Now "Dogs vs Cats" dataset can be read from TensorBay.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:dataset` "Dogs vs Cats", there are two
:ref:`segments <reference/dataset_structure:segment>`: ``train`` and ``test``.
Get the segment names by listing them all.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / list segment names"""
   :end-before: """"""

Get a segment by passing the required segment name.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the train :ref:`reference/dataset_structure:segment`, there is a sequence of :ref:`reference/dataset_structure:data`,
which can be obtained by index.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:data`,
there is a sequence of :ref:`reference/label_format:Classification` annotations,
which can be obtained by index.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "Dogs vs Cats" dataset, which is ``classification``. The information stored in :ref:`reference/label_format:category` is
one of the names in "categories" list of :ref:`catalog.json <dogsvscats-catalog>`.
See :ref:`reference/label_format:Classification` label format for more details.

****************
 Delete Dataset
****************

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
