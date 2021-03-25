###############
 20 Newsgroups
###############

This topic describes how to manage the "20 Newsgroups" dataset.

"20 Newsgroups" is a dataset with :ref:`reference/label_format:Classification` label type.
See `this page <https://www.graviti.cn/open-datasets/data-decorators/Newsgroups20>`_ for more details about this dataset.

***************************
 Authorize a Client Object
***************************

First of all, create a GAS client.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Authorize a Client Object"""
   :end-before: """"""

****************
 Create Dataset
****************
  
Then, create a dataset client by passing the dataset name to the GAS client.
  
.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

********************
 List Dataset Names
********************
    
To check if you have created "20 Newsgroups" dataset, you can list all your available datasets.
See :ref:`this page <features/dataset_management:Read Dataset>` for details.
    
.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """List Dataset Names"""
   :end-before: """"""
    
.. note::
    
   Note that method ``list_dataset_names()`` returns an iterator, use ``list()`` to transfer it to a "list".

******************
 Organize Dataset
******************
  
Now we describe how to organize the "20 Newsgroups" dataset by the :class:`~tensorbay.dataset.dataset.Dataset`
object before uploading it to TensorBay. It takes the following steps to organize "20 Newsgroups".

Write the Catalog
=================

The first step is to write the :ref:`reference/dataset_structure:Catalog`.
Catalog is a json file contains all label information of one dataset.
See :ref:`this page <reference/dataset_structure:Catalog>` for more details.
The only annotation type for "20 Newsgroups" is :ref:`reference/label_format:Classification`,
and there are 20 :ref:`reference/label_format:Category` types.

.. literalinclude:: ../../../tensorbay/opendataset/Newsgroups20/catalog.json
   :language: json
   :name: Newsgroups20-catalog
   :linenos:

.. note::
   The :ref:`categories<reference/label_format:Category>` in
   :ref:`reference/dataset_structure:Dataset` "20 Newsgroups" have parent-child relationship,
   and it use "." to sparate different levels.

Write the Dataloader
====================

The second step is to write the :ref:`reference/glossary:Dataloader`.
The function of :ref:`reference/glossary:Dataloader` is to read the dataset into a
:class:`~tensorbay.dataset.dataset.Dataset` object.
The :ref:`code block <Newsgroups20-dataloader>` below displays the "20 Newsgroups" dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/Newsgroups20/loader.py
   :language: python
   :name: Newsgroups20-dataloader
   :linenos:
   :emphasize-lines: 11-12, 77, 92

Note that after creating the :ref:`reference/dataset_structure:Dataset`,
you need to load the :ref:`reference/dataset_structure:catalog`. (L77)
The catalog file "catalog.json" is in the same directory with dataloader file.

In this example, we create segments by ``dataset.create_segment(SEGMENT_NAME)``.
You can also create a default segment without giving a specific name, then its name
will be "".

See :ref:`this page <reference/label_format:Classification>` for more details for
about Classification annotation details.

.. note::
   The :ref:`20 Newsgroups dataloader <Newsgroups20-dataloader>` above uses relative import(L11-12).
   However, when you write your own dataloader you should use regular import as shown below.
   And when you want to contribute your own dataloader, remember to use relative import.

.. note::
   The data in "20 Newsgroups" do not have extensions
   so that we add a "txt" extension to the remote path of each data file(L92)
   to ensure the loaded dataset could function well on TensorBay.

****************
 Upload Dataset
****************

After you finish the :ref:`reference/glossary:Dataloader` and organize the "20 Newsgroups" into a
:class:`~tensorbay.dataset.dataset.Dataset` object, you can upload it
to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Remember to execute the commit step after uploading.
If needed, you can re-upload and commit again.
Please see :ref:`this page <features/version_control:Version Control>` for more details about version control.

.. note::

   Commit operation can also be done on our GAS_ Platform.

.. _gas: https://www.graviti.cn/tensorBay

**************
 Read Dataset
**************

Now you can read "20 Newsgroups" dataset from TensorBay.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "20 Newsgroups", there are four
:ref:`Segments <reference/dataset_structure:Segment>`: ``20news-18828``,
``20news-bydate-test`` and ``20news-bydate-train``, ``20_newsgroups``
you can get the segment names by list them all.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / list segment names"""
   :end-before: """"""

You can get a segment by passing the required segment name.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the 20news-18828 :ref:`reference/dataset_structure:Segment`, there is a sequence of :ref:`reference/dataset_structure:Data`. You
can get one by index.

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

.. note::

   If the :ref:`reference/dataset_structure:Segment` or
   :ref:`advanced_features/fusion_dataset/fusion_dataset_structure:fusion segment`
   is created  without given name, then its name will be "".

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Classification` annotations.
You can get one by index.

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

To delete "20 Newsgroups", run the following code:

.. literalinclude:: ../../../examples/Newsgroups20.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
