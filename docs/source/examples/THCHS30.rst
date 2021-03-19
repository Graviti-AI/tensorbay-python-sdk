###########
 THCHS-30
###########

This topic describes how to manage the "THCHS-30" dataset.

"THCHS-30" is a dataset with :ref:`reference/label_format:Sentence` label type. 
See `this page <https://www.graviti.com/open-datasets/THCHS30>`_ for more details about this dataset.

***************************
 Authorize a Client Object
***************************

First of all, create a GAS client.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Authorize a Client Object"""
   :end-before: """"""

****************
 Create Dataset
****************

Then, create a dataset client by passing the dataset name to the GAS client.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

********************
List Dataset Names
********************

To check if you have created "THCHS-30" dataset, you can list all your available datasets.
See :ref:`this page <features/dataset_management:Read Dataset>` for details.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """List Dataset Names"""
   :end-before: """"""

.. note::

    Note that method ``list_dataset_names()`` returns an iterator, use ``list()`` to transfer it to a "list".

******************
Organize Dataset
******************

Now we describe how to organize the "THCHS-30" dataset by the :class:`~tensorbay.dataset.dataset.Dataset`
object before uploading it to TensorBay. It takes the following steps to organize "THCHS-30".

Write the Catalog
=================

The first step is to write the :ref:`reference/dataset_structure:Catalog`.
Typically, Catalog is a json file contains all label information of one dataset.
See :ref:`this page <reference/dataset_structure:Catalog>` for more details.
However the catalog of ``THCHS-30`` is too large, so we need to load the subcatalog by the raw file
and map it to catalog, See :ref:`code block <THCHS30-dataloader>` below for more details.

Write the Dataloader
====================

The second step is to write the :ref:`reference/glossary:Dataloader`.
The function of :ref:`reference/glossary:Dataloader` is to read the dataset into a
:class:`~tensorbay.dataset.dataset.Dataset` object.
The :ref:`code block <THCHS30-dataloader>` below displays the "THCHS-30" dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/THCHS30/loader.py
   :language: python
   :name: THCHS30-dataloader
   :linenos:
   :emphasize-lines: 13-14, 45

Normally, after creating the :ref:`reference/dataset_structure:Dataset`,
you need to load the :ref:`reference/dataset_structure:catalog`. However, 
in this example, there is no ``catalog.json`` file, because the lexion of
``THCHS-30`` is too large (See more details of lexion in :ref:`reference/label_format:Sentence`).
Therefore, We load subcatalog from the raw file lexicon.txt and map it to have the catalog.(L45)

See :ref:`this page <reference/label_format:Sentence>` for more details
about Sentence annotation details.

.. note::
    The :ref:`THCHS-30 dataloader <THCHS30-dataloader>` above uses relative import(L13-14).
    However, when you write your own dataloader you should use regular import.
    And when you want to contribute your own dataloader, remember to use relative import.

****************
Upload Dataset
****************

After you finish the :ref:`reference/glossary:Dataloader` and organize the "THCHS-30" into a
:class:`~tensorbay.dataset.dataset.Dataset` object, you can upload it
to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Remember to execute the :ref:`features/version_control:Commit` step after uploading.
If needed, you can re-upload and commit again.
Please see :ref:`features/version_control:Version Control` for more details.

.. note::

    Commit operation can alse be done on our GAS_ Platform.
 
 .. _gas: https://www.graviti.cn/tensorBay

**************
Read Dataset
**************

Now you can read "THCHS-30" dataset from TensorBay.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "THCHS-30", there are three
:ref:`Segments <reference/dataset_structure:Segment>`:
``dev``, ``train`` and ``test``,
you can get the segment names by list them all.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Read Dataset / list segment names"""
   :end-before: """"""

You can get a segment by passing the required segment name.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the dev :ref:`reference/dataset_structure:Segment`,
there is a sequence of :ref:`reference/dataset_structure:Data`.
You can get one by index.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

.. note::

    If the :ref:`reference/dataset_structure:Segment` or
    :ref:`advanced_features/fusion_dataset/fusion_dataset_structure:fusion segment`
    is created without given name, then its name will be "".

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Sentence` annotations.
You can get one by index.

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "THCHS-30" dataset, which is ``Sentence``. It contains
``sentence``, ``spell`` and ``phone`` information. See :ref:`this page <reference/label_format:Sentence>` for 
more details about the structure of Sentence.

****************
Delete Dataset
****************

To delete "THCHS-30", run the following code:

.. literalinclude:: ../../../examples/thchs30.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""