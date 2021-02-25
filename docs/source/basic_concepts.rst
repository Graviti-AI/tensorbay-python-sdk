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

:class:`~graviti.dataset.dataset.Dataset` is one of the two topmost data levels
in the TensorBay dataset structure.
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

:class:`~graviti.dataset.dataset.FusionDataset`
represents datasets with data collected from multiple sensors,
and is often used for autonomous driving datasets, such as `nuScenes`_ and `KITTI-tracking`_.

See :ref:`basic_concepts:Dataset` for the comparison between
:class:`~graviti.dataset.dataset.Dataset` and :class:`~graviti.dataset.dataset.FusionDataset`.

The structure of a :class:`~graviti.dataset.dataset.Dataset` looks like:

.. code:: console
   :name: fusion-dataset-structure

   FusionDataset
   ├── Catalog
   │   ├── SubCatalog
   │   ├── SubCatalog
   │   └── ...
   ├── FusionSegment
   │   ├── sensors
   │   │   ├── Sensor
   │   │   ├── Sensor
   │   │   └── ...
   │   ├── Frame
   │   │   ├── Data
   │   │   └── ...
   │   ├── Frame
   │   │   ├── Data
   │   │   └── ...
   │   └── ...
   ├── FusionSegment
   └── ...

.. _nuScenes: https://www.graviti.cn/open-datasets/nuScenes
.. _KITTI-tracking: https://www.graviti.cn/open-datasets/KITTItracking


FusionDataset
=============

:class:`~graviti.dataset.dataset.FusionDataset` is one of the two topmost data levels
in the TensorBay dataset structure.

It is made up of data collected from multiple sensors
and contains all the frames, labels, sensors and any other information of a fusion dataset.

There are a certain number of :class:`FusionSegments <graviti.dataset.segment.FusionSegment>`
in one :class:`~graviti.dataset.dataset.FusionDataset`.

FusionSegment
=============

:class:`~graviti.dataset.segment.FusionSegment` is the data level second to
:class:`~graviti.dataset.dataset.FusionDataset` in the TensorBay dataset structure.

Each :class:`~graviti.dataset.segment.FusionSegment` consists of
a certain number of :class:`Frames<graviti.dataset.frame.Frame>` to store the data.

Besides, a fusion segment contains multiple :class:`Sensors<graviti.sensor.sensor.Sensor>`
from which the :class:`~graviti.dataset.data.Data`
under each :class:`~graviti.dataset.frame.Frame` are collected.

Sensor
======

:class:`~graviti.sensor.sensor.Sensor` represents the device that collects the data
in the :class:`~graviti.dataset.segment.FusionSegment`.

Currently, We support four types of :class:`Sensors<graviti.sensor.sensor.Sensor>`.

.. table:: supported sensors
   :widths: auto

   =============================================  ===================================
   supported sensors                              corresponding data type
   =============================================  ===================================
   :class:`~graviti.sensor.sensor.Camera`         image
   :class:`~graviti.sensor.sensor.FisheyeCamera`  image
   :class:`~graviti.sensor.sensor.Lidar`          point cloud
   :class:`~graviti.sensor.sensor.Radar`          point cloud
   =============================================  ===================================

A :class:`~graviti.sensor.sensor.Sensor` object stores the information of a sensor,
including the sensor name,
extrinsic parameters and intrinsic parameters(only for camera type sensors).

Frame
=====

:class:`~graviti.dataset.frame.Frame` is the component
that composes :class:`~graviti.dataset.segment.FusionSegment`.

A :class:`~graviti.dataset.frame.Frame` object consists of
multiple :class:`~graviti.dataset.data.Data` collected at the same time from different sensors.

Data in FusionDataset
=====================

Each :class:`data<graviti.dataset.data.Data>` inside a :class:`frame<graviti.dataset.frame.Frame>`
corresponds to a :class:`sensor<graviti.sensor.sensor.Sensor>`.

And the :class:`~graviti.dataset.data.Data` in :class:`~graviti.dataset.dataset.FusionDataset`
is the same as the :ref:`basic_concepts:Data` in :class:`~graviti.dataset.dataset.Dataset`.
