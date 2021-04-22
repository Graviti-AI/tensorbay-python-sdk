###########
 THCHS-30
###########

This topic describes how to manage the `THCHS-30 Dataset`_,
which is a dataset with :ref:`reference/label_format:Sentence` label

.. _THCHS-30 Dataset: https://www.graviti.com/open-datasets/data-decorators/THCHS30

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
Organize Dataset
******************

It takes the following steps to organize the “THCHS-30” dataset by the :class:`~tensorbay.dataset.dataset.Dataset` instance.

Step 1: Write the Catalog
=========================

A :ref:`Catalog <reference/dataset_structure:catalog>` contains all label information of one
dataset, which is typically stored in a json file. However the catalog of THCHS-30 is too
large, instead of reading it from json file, we read it by mapping from subcatalog that is
loaded by the raw file. Check the :ref:`dataloader <THCHS30-dataloader>` below for more details.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different
   label types.

Step 2: Write the Dataloader
============================

A :ref:`dataloader <THCHS30-dataloader>` is needed to organize the dataset
into a :class:`~tensorbay.dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../tensorbay/opendataset/THCHS30/loader.py
   :language: python
   :name: THCHS30-dataloader
   :linenos:

See :ref:`Sentence annotation <reference/label_format:Sentence>` for more details.

.. note::
    Since the :ref:`THCHS-30 dataloader <THCHS30-dataloader>` above is already included in TensorBay,
    so it uses relative import.
    However, the regular import should be used when writing a new dataloader.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Organize Dataset / regular import"""
   :end-at: from tensorbay.label import LabeledSentence, SentenceSubcatalog, Word

There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, importing an available dataloadert is also feasible.

.. literalinclude:: ../../../examples/THCHS30.py
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

The organized "THCHS-30" dataset can be uploaded to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :ref:`features/version_control:Version Control` for more details.

**************
Read Dataset
**************

Now "THCHS-30" dataset can be read from TensorBay.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

In :ref:`reference/dataset_structure:Dataset` "THCHS-30", there are three
:ref:`Segments <reference/dataset_structure:Segment>`:
``dev``, ``train`` and ``test``.
Get the segment names by listing them all.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Read Dataset / list segment names"""
   :end-before: """"""

Get a segment by passing the required segment name.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the dev :ref:`reference/dataset_structure:Segment`,
there is a sequence of :ref:`reference/dataset_structure:Data`,
which can be obtained by index.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:Data`,
there is a sequence of :ref:`reference/label_format:Sentence` annotations,
which can be obtained by index.

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "THCHS-30" dataset, which is ``Sentence``. It contains
``sentence``, ``spell`` and ``phone`` information. See :ref:`Sentence <reference/label_format:Sentence>`
label format for more details.

****************
Delete Dataset
****************

.. literalinclude:: ../../../examples/THCHS30.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
