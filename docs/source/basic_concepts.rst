################
 Basic Concepts
################

In this chapter, we explain the related concepts of a dataset structure in TensorBay format.
There are mainly two types of datasets: :ref:`Dataset <basic_concepts:Dataset Related Concepts>`
and :ref:`FusionDataset <basic_concepts:FusionDataset Related Concepts>`.

**************************
 Dataset Related Concepts
**************************

:class:`~graviti.dataset.dataset.Dataset` represents the most common dataset
such as `MNIST`_ and `THUCNews`_.
It is made up of data collected from only one sensor or data without sensor information.
See :ref:`basic_concepts:FusionDataset` for the comparison between
:class:`~graviti.dataset.dataset.Dataset` and :class:`~graviti.dataset.dataset.FusionDataset`.

The structure of a :class:`~graviti.dataset.dataset.Dataset` looks like:

.. code:: console
   :name: dataset-structure

   Dataset
   ├── Catalog
   │   ├── SubCatalog
   │   ├── SubCatalog
   │   └── ...
   ├── Segment
   │   ├── Data
   │   ├── Data
   │   └── ...
   └── Segment
       ├── Data
       ├── Data
       └── ...

.. _MNIST: https://www.graviti.cn/open-datasets/MNIST
.. _THUCNews: https://www.graviti.cn/open-datasets/THUCNews

Dataset
=======

:class:`~graviti.dataset.dataset.Dataset` is the topmost data level in the TensorBay dataset
structure.
It contains all the data, label and any other information of a dataset.

There are a certain number of :class:`Segments <graviti.dataset.segment.Segment>`
in one :class:`~graviti.dataset.dataset.Dataset`.

Catalog & SubCatalog
====================

Catalog stores the label meta information.
It collects all the labels occurred in all data samples of a dataset.
There could be one or several SubCatalogs under one Catalog,
each of which only stores label meta information of one type.
Code block below is the Catalog of dataset `Neolix OD`_.

.. _Neolix OD: https://www.graviti.cn/open-datasets/NeolixOD

.. literalinclude:: ../../tensorbay/opendataset/NeolixOD/catalog.json
   :language: json
   :name: NeolixOD-catalog
   :linenos:

Segment
=======

:class:`~graviti.dataset.segment.Segment` is the data level second to
:class:`~graviti.dataset.dataset.Dataset` in the TensorBay dataset structure.
Each :class:`~graviti.dataset.segment.Segment` contains a certain number of
:class:`~graviti.dataset.data.Data`.
For example, all training samples can be organized in one :class:`~graviti.dataset.segment.Segment`.

Data
====

:class:`~graviti.dataset.data.Data` is the most basic data level in the TensorBay dataset structure.
A :class:`~graviti.dataset.data.Data` object contains one dataset sample and its related labels
and any other information such as timestamp.

********************************
 FusionDataset Related Concepts
********************************

FusionDataset
=============

FusionSegment
=============

Frame
=====

Sensor
======

Data in FusionDataset
=====================
