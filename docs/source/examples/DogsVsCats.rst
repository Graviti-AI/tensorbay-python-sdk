##############
 Dogs vs Cats
##############

This topic describes how to manage the "Dogs vs Cats" dataset.

"Dogs vs Cats" is a dataset with :ref:`reference/label_format:Classification` label type.
See `this page <https://gas.graviti.cn/dataset/data-decorators/DogsVsCats>`_  for more details about this dataset.

***************************
 Authorize a Client Object
***************************

First of all, create a GAS client.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Authorize a Client Object"""
   :end-before: """"""

****************
 Create Dataset
****************

Then, create a dataset client by passing the dataset name to the GAS client.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

********************
 List Dataset Names
********************

List all the available datasets to check if the "Dogs vs Cats" dataset have been created.
See :ref:`this page <features/dataset_management:Read Dataset>` for details.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """List Dataset Names"""
   :end-before: """"""

.. note::

   Note that method ``list_dataset_names()`` returns an iterator, use ``list()`` to transfer it to a "list".

******************
 Organize Dataset
******************

This part describes how to organize the "Dogs vs Cats" dataset by the :class:`~tensorbay.dataset.dataset.Dataset`
object before uploading it to TensorBay. It takes the following steps to organize "Dogs vs Cats".

Write the Catalog
=================

The first step is to write the catalog(:ref:`ref <reference/dataset_structure:Catalog>`).
Catalog is a json file contains all label information of one dataset.
The only annotation type for "Dogs vs Cats" is :ref:`reference/label_format:Classification`, and there are 2
:ref:`reference/label_format:Category` types.

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/catalog.json
   :language: json
   :name: dogsvscats-catalog
   :linenos:

.. important::

   See :ref:`this part <reference/dataset_structure:Catalog>` for more examples of catalogs with different label types.

Write the Dataloader
====================

The second step is to write the :ref:`reference/glossary:Dataloader`.
The function of :ref:`reference/glossary:Dataloader` is to read the dataset into a
:class:`~tensorbay.dataset.dataset.Dataset` object.
The :ref:`code block <BSTLD-dataloader>` below displays the "Dogs vs Cats" dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/loader.py
   :language: python
   :name: dogsvscats-dataloader
   :linenos:
   :emphasize-lines: 11-12,43

Note that after the :ref:`reference/dataset_structure:Dataset` is created,
the :ref:`reference/dataset_structure:catalog` needs to be loaded.(L43)
The catalog file "catalog.json" is in the same directory with dataloader file.

In this example, segments are created by ``dataset.create_segment(SEGMENT_NAME)``.
A default segment can also be created without giving a specific name, then its name
will be "".

See :ref:`this page <reference/label_format:Classification>` for more details for about Classification annotation details.

.. note::

   The :ref:`Dogs vs Cats dataloader <dogsvscats-dataloader>` above uses relative import(L11-12).
   However, use regular import when writing your own dataloader.
   And use relative import when contributing the dataloader.

.. important::

   See :ref:`this part <reference/glossary:Dataloader>` for more examples of dataloaders with different label types.

****************
 Upload Dataset
****************

After finishing the :ref:`reference/glossary:Dataloader` and organize the "Dogs vs Cats" into a
:class:`~tensorbay.dataset.dataset.Dataset` object, upload it
to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Remember to execute the commit step after uploading.
If needed, re-upload and commit again.
Please see :ref:`this page <features/version_control:Version Control>` for more details about version control.

.. note::

   Commit operation can also be done on our GAS_ Platform.

.. _gas: https://www.graviti.cn/tensorBay

**************
 Read Dataset
**************

Now "Dogs vs Cats" dataset can be read from TensorBay.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "Dogs vs Cats", there are two
:ref:`Segments <reference/dataset_structure:Segment>`: ``train`` and ``test``.
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


In the train :ref:`reference/dataset_structure:Segment`, there is a sequence of :ref:`reference/dataset_structure:Data`,
which can be obtained by index.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

.. note::

   If the :ref:`reference/dataset_structure:Segment` or
   :ref:`advanced_features/fusion_dataset/fusion_dataset_structure:fusion segment`
   is created  without given name, then its name will be "".

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Classification` annotations,
which can be obtained by index.

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "Dogs vs Cats" dataset, which is ``classification``. The information stored in :ref:`reference/label_format:Category` is
one of the category names in "categories" list of :ref:`catalog.json <dogsvscats-catalog>`.
See :ref:`this page <reference/label_format:Classification>` for more details about the
structure of Classification.

****************
 Delete Dataset
****************

To delete "Dogs vs Cats", run the following code:

.. literalinclude:: ../../../examples/DogsVsCats.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
