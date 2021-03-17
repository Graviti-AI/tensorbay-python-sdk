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
please see :ref:`SDK authorization<quick_start/getting_started_with_tensorbay:Authorize a Client Object>`
or :ref:`CLI configration<tensorbay_cli/getting_started_with_cli:config>`.

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

.. code:: python

   from tensorbay.dataset import Dataset

   def dataset_name(path: str):
       dataset = Dataset("dataset_name")
       # organize the files( and the labels) under the path to the dataset
       ...
       return dataset

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

An operation to turn a dataset from draft status to committed status.

After commit, the committed version of the dataset can no longer be changed.
But you can edit the draft version of the dataset based on this commit.

Commit is a basic operation in version control on Tensorbay.
Learn more about version control in :ref:`features/version_control:Version Control`.
