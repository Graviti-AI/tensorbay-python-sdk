###############
 Dogs vs. Cats
###############

This topic describes how to manage the "Dogs vs. Cats" dataset.

"Dogs vs. Cats" is a dataset with :ref:`reference/label_format:Classification` label type.
See `this page <https://www.graviti.cn/open-datasets/DogsVsCats>`_  for more details about this dataset.

***************************
 Authorize a Client Object
***************************

First of all, create a GAS client.

.. code:: python

   from tensorbay import GAS

   ACCESS_KEY = "Accesskey-*****"
   gas = GAS(ACCESS_KEY)

****************
 Create Dataset
****************

Then, create a dataset client by passing the dataset name to the GAS client.

.. code:: python

   gas.create_dataset("Dogs vs. Cats")

********************
 List Dataset Names
********************

To check if you have created "Dogs vs. Cats" dataset, you can list all your available datasets.
See :ref:`this page <features/dataset_management:Read Dataset>` for details.

.. code:: python

   list(gas.list_dataset_names())

.. note::

   Note that method ``list_dataset_names()`` returns an iterator, use ``list()`` to transfer it to a "list".

******************
 Organize Dataset
******************

Now we describe how to organize the "Dogs vs. Cats" dataset by the :class:`~tensorbay.dataset.dataset.Dataset`
object before uploading it to TensorBay. It takes the following steps to organize "Dogs vs. Cats".

Write the Catalog
=================

The first step is to write the :ref:`reference/dataset_structure:Catalog`.
Catalog is a json file contains all label information of one dataset.
See :ref:`this page <reference/dataset_structure:Catalog>` for more details.
The only annotation type for "Dogs vs. Cats" is :ref:`reference/label_format:Classification`, and there are 2
:ref:`reference/label_format:Category` types.

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/catalog.json
   :language: json
   :name: dogsvscats-catalog
   :linenos:

Write the Dataloader
====================

The second step is to write the :ref:`reference/glossary:Dataloader`.
The function of :ref:`reference/glossary:Dataloader` is to read the dataset into a
:class:`~tensorbay.dataset.dataset.Dataset` object.
The :ref:`code block <BSTLD-dataloader>` below displays the "Dogs vs. Cats" dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/loader.py
   :language: python
   :name: dogsvscats-dataloader
   :linenos:
   :emphasize-lines: 11-12,43

Note that after creating the :ref:`reference/dataset_structure:Dataset`,
you need to load the :ref:`reference/dataset_structure:catalog`.(L43)
The catalog file "catalog.json" is in the same directory with dataloader file.

In this example, we create segments by ``dataset.create_segment(SEGMENT_NAME)``.
You can also create a default segment without giving a specific name, then its name
will be "".

See :ref:`this page <reference/label_format:Classification>` for more details for about Classification annotation details.

.. note::
   The :ref:`BSTLD dataloader <BSTLD-dataloader>` above uses relative import(L11-12).
   However, when you write your own dataloader you should use regular import.
   And when you want to contribute your own dataloader, remember to use relative import.

****************
 Upload Dataset
****************

After you finish the :ref:`reference/glossary:Dataloader` and organize the "Dogs vs. Cats" into a
:class:`~tensorbay.dataset.dataset.Dataset` object, you can upload it
to TensorBay for sharing, reuse, etc.

.. code:: python

   # dataset is the one you initialized in "Organize Dataset" section
   dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=False)
   dataset_client.commit("Dogs vs. Cats")

**************
 Read Dataset
**************

Now you can read "Dogs vs. Cats" dataset from TensorBay.

.. code:: python

   dataset_client = gas.get_dataset("Dogs vs. Cats")

In :ref:`reference/dataset_structure:Dataset` "Dogs vs. Cats", there are two
:ref:`Segments <reference/dataset_structure:Segment>`: ``train`` and ``test``,
you can get the segment names by list them all.

.. code:: python

   list(dataset_client.list_segment_names())

You can get a segment by passing the required segment name.

.. code:: python

   from tensorbay.dataset import Segment

   train_segment = Segment("train", dataset_client)


In the train :ref:`reference/dataset_structure:Segment`, there is a sequence of :ref:`reference/dataset_structure:Data`. You
can get one by index.

.. code:: python

   data = train_segment[0]

.. note::

   If the :ref:`reference/dataset_structure:Segment` or
   :ref:`advanced_features/fusion_dataset/fusion_dataset_structure:fusion segment`
   is created  without given name, then its name will be "".

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Classification` annotations.
You can get one by index.

.. code:: python

   category = data.label.classification.category

There is only one label type in "Dogs vs. Cats" dataset, which is ``classification``. The information stored in :ref:`reference/label_format:Category` is
one of the category names in "categories" list of :ref:`catalog.json <dogsvscats-catalog>`.
See :ref:`this page <reference/label_format:Classification>` for more details about the
structure of Classification.

****************
 Delete Dataset
****************

To delete "Dogs vs. Cats", run the following code:

.. code:: python

   gas.delete_dataset("BSTLD")