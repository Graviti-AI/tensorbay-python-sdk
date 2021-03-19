#################
 LeedsSportsPose
#################

This topic describes how to manage the "LeedsSportsPose" dataset.

"LeedsSportsPose" is a dataset with :ref:`reference/label_format:Keypoints2D` label type (:numref:`Fig. %s <example-leedssportspose>`).
See `this page <https://www.graviti.cn/open-datasets/LeedsSportsPose>`_  for more details about this dataset.

.. _example-leedssportspose:

.. figure:: ../images/example-Keypoints2D.png
   :scale: 80 %
   :align: center

   The preview of an image with labels from "LeedsSportsPose".

***************************
 Authorize a Client Object
***************************

First of all, create a GAS client.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Authorize a Client Object"""
   :end-before: """"""

****************
 Create Dataset
****************

Then, create a dataset client by passing the dataset name to the GAS client.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

********************
 List Dataset Names
********************

To check if you have created "LeedsSportsPose" dataset, you can list all your available datasets.
See :ref:`this page <features/dataset_management:Read Dataset>` for details.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """List Dataset Names"""
   :end-before: """"""

.. note::

   Note that method ``list_dataset_names()`` returns an iterator, use ``list()`` to transfer it to a "list".

******************
 Organize Dataset
******************

Now we describe how to organize the "LeedsSportsPose" dataset by the :class:`~tensorbay.dataset.dataset.Dataset`
object before uploading it to TensorBay. It takes the following steps to organize "LeedsSportsPose".

Write the Catalog
=================

The first step is to write the :ref:`reference/dataset_structure:Catalog`.
Catalog is a json file contains all label information of one dataset.
See :ref:`this page <reference/dataset_structure:Catalog>` for more details.
The only annotation type for "LeedsSportsPose" is :ref:`reference/label_format:Keypoints2D`.

.. literalinclude:: ../../../tensorbay/opendataset/LeedsSportsPose/catalog.json
   :language: json
   :name: LeedsSportsPose-catalog
   :linenos:

Write the Dataloader
====================

The second step is to write the :ref:`reference/glossary:Dataloader`.
The function of :ref:`reference/glossary:Dataloader` is to read the dataset into a
:class:`~tensorbay.dataset.dataset.Dataset` object.
The :ref:`code block <LeedsSportsPose-dataloader>` below displays the "LeedsSportsPose" dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/LeedsSportsPose/loader.py
   :language: python
   :name: LeedsSportsPose-dataloader
   :linenos:
   :emphasize-lines: 11-13,42

Note that after creating the :ref:`reference/dataset_structure:Dataset`,
you need to load the :ref:`reference/dataset_structure:catalog`.(L42)
The catalog file "catalog.json" is in the same directory with dataloader file.

In this example, we create a default segment without giving a specific name.
You can also create a segment by ``dataset.create_segment(SEGMENT_NAME)``.

See :ref:`this page <reference/label_format:Keypoints2D>` for more details for about Keypoints2D annotation details.

.. note::
   The :ref:`LeedsSportsPose dataloader <LeedsSportsPose-dataloader>` above uses relative import(L11-13).
   However, when you write your own dataloader you should use regular import.
   And when you want to contribute your own dataloader, remember to use relative import.

****************
 Upload Dataset
****************

After you finish the :ref:`reference/glossary:Dataloader` and organize the "LeedsSportsPose" into a
:class:`~tensorbay.dataset.dataset.Dataset` object, you can upload it
to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Remember to execute the :ref:`features/version_control:Commit` step after uploading.
If needed, you can re-upload and commit again.
Please see :ref:`this page <features/version_control:Version Control>` for more details about version control.

.. note::

   Commit operation can also be done on our GAS_ Platform.

.. _gas: https://www.graviti.cn/tensorBay

**************
 Read Dataset
**************

Now you can read "LeedsSportsPose" dataset from TensorBay.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "LeedsSportsPose", there is one default
:ref:`Segments <reference/dataset_structure:Segment>` ``""`` (empty string). You can get it by passing the segment name.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the train :ref:`reference/dataset_structure:Segment`, there is a sequence of :ref:`reference/dataset_structure:Data`. You
can get one by index.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

.. note::

   If the :ref:`reference/dataset_structure:Segment` or
   :ref:`advanced_features/fusion_dataset/fusion_dataset_structure:fusion segment`
   is created  without given name, then its name will be "".

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Keypoints2D` annotations.
You can get one by index.

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "LeedsSportsPose" dataset, which is ``keypoints2d``. The information stored in ``x`` (``y``) is
the x (y) coordinate of one keypoint of one keypoints list. The information stored in ``v`` is
the visible status of one keypoint of one keypoints list. See :ref:`this page <reference/label_format:Keypoints2D>`
for more details about the structure of Keypoints2D.

****************
 Delete Dataset
****************

To delete "LeedsSportsPose", run the following code:

.. literalinclude:: ../../../examples/leedssportspose.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
