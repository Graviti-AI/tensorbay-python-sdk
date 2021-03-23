##########
 Glossary
##########

accesskey
=========

An accesskey is an access credential for identification when using TensorBay to operate on your dataset.

To obtain an accesskey, you need to log in to `Graviti AI Service(GAS)`_ and
visit the `developer page <https://gas.graviti.cn/access-key>`_ to create one.

.. _graviti ai service(gas): https://www.graviti.cn/tensorBay

For the usage of accesskey via Tensorbay SDK or CLI,
please see :ref:`SDK authorization <quick_start/getting_started_with_tensorbay:Authorize a Client Object>`
or :ref:`CLI configration <tensorbay_cli/getting_started_with_cli:Configuration>`.

dataset
=======

A uniform dataset format defined by Tensorbay,
which only contains one type of data collected from one sensor or without sensor information.

The corresponding class of dataset is :class:`~tensorbay.dataset.dataset.Dataset`.

See :ref:`reference/dataset_structure:Dataset Structure` for more details.

fusion dataset
==============

A uniform dataset format defined by Tensorbay,
which contains data collected from multiple sensors.

The corresponding class of fusion dataset is :class:`~tensorbay.dataset.dataset.FusionDataset`.

See :ref:`advanced_features/fusion_dataset/fusion_dataset_structure:Fusion Dataset Structure` for more details.

dataloader
==========

A function that can organize files within a formatted folder
into a :class:`~tensorbay.dataset.dataset.Dataset` instance
or a :class:`~tensorbay.dataset.dataset.FusionDataset` instance.

The only input of the function should be a str indicating the path to the folder containing the dataset,
and the return value should be the loaded :class:`~tensorbay.dataset.dataset.Dataset`
or :class:`~tensorbay.dataset.dataset.FusionDataset` instance.

.. literalinclude:: ../../../examples/glossary.py
      :language: python
      :start-after: """dataloader"""
      :end-before: """"""

.. note::

  The name of the dataloader function is a unique indentification of the dataset.
  It is in upper camel case and is generally obtained by removing special characters from the dataset name.

  Take `Dogs vs Cats`_ dataset as an example,
  the name of its dataloader function is :meth:`~tensorbay.opendataset.DogsVsCats.loader.DogsVsCats`.

  .. _dogs vs cats: https://www.graviti.cn/open-datasets/DogsVsCats

See more dataloader examples in :ref:`api/opendataset/opendataset_module:tensorbay.opendataset`.

TBRN
====

TBRN is the abbreviation for TensorBay Resource Name, which represents the data or a collection of data stored in TensorBay uniquely.

Note that TBRN is only used in :ref:`CLI<tensorbay_cli/getting_started_with_cli:Getting Started with CLI>`.

TBRN begins with ``tb:``, followed by the dataset name, the segment name and the file name.

The following is the general format for TBRN:

.. code::

    tb:[dataset_name]:[segment_name]://[remote_path]

Suppose we have an image ``000000.jpg`` under the default segment of a dataset named ``example``,
then we have the TBRN of this image:

.. code::

    tb:example:://000000.jpg

.. note::

   Default segment is defined as ``""`` (empty string).


commit
======

Similar with Git, a commit is a version of a dataset,
which contains the changes compared with the former commit.
You can view a certain commit of a dataset based on the given commit ID.

A commit is readable, but is not writable.
Thus, only read operations such as getting catalog, files and labels are allowed.
To change a dataset, please create a new commit.
See :ref:`reference/glossary:draft` for details.

On the other hand,
"commit" also represents the action to save the changes inside a :ref:`reference/glossary:draft` into a commit.

draft
=====

Similar with Git, a draft is a workspace in which changing the dataset is allowed.

A draft is created based on a :ref:`reference/glossary:commit`,
and the changes inside it will be made into a commit.

There are scenarios when modifications of a dataset are required,
such as correcting errors, enlarging dataset, adding more types of labels, etc.
Under these circumstances, you can create a draft, edit the dataset and commit the draft.
