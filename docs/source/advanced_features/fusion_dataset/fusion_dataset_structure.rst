##########################
 Fusion Dataset Structure
##########################

TensorBay also defines a uniform fusion dataset format.
In this topic, we explain the related concepts.
The TensorBay fusion dataset format looks like::

   fusion dataset
   ├── catalog
   │   ├── subcatalog
   │   ├── subcatalog
   │   └── ...
   ├── fusion segment
   │   ├── sensors
   │   │   ├── sensor
   │   │   ├── sensor
   │   │   └── ...
   │   ├── frame
   │   │   ├── data
   │   │   └── ...
   │   ├── frame
   │   │   ├── data
   │   │   └── ...
   │   └── ...
   ├── fusion segment
   └── ...

****************
 fusion dataset
****************

Fusion dataset is the topmost concept in TensorBay format.
Each fusion dataset includes a catalog and a certain number of fusion segments.

The corresponding class of fusion dataset is :class:`~tensorbay.dataset.dataset.FusionDataset`.

****************************************
 catalog & subcatalog in fusion dataset
****************************************

The catalog of the fusion dataset is the same as the catalog
(:ref:`ref <basic_concepts:catalog & subcatalog>`) of the dataset.

****************
 fusion segment
****************

There may be several parts in a fusion dataset.
In TensorBay format, each part of the fusion dataset is stored in one fusion segment.
Each fusion segment contains a certain number of frames and multiple sensors,
from which the data inside the fusion segment are collected.

The corresponding class of fusion segment is :class:`~tensorbay.dataset.segment.FusionSegment`.

********
 sensor
********

Sensor represents the device that collects the data inside the fusion segment.
Currently, TensorBay supports four sensor types.(:numref:`Table. %s <sensor_types>`)

.. _sensor_types:

.. table:: supported sensors
   :widths: auto

   ===============================================  =================================
   Supported Sensors                                Corresponding Data Type
   ===============================================  =================================
   :class:`~tensorbay.sensor.sensor.Camera`         image
   :class:`~tensorbay.sensor.sensor.FisheyeCamera`  image
   :class:`~tensorbay.sensor.sensor.Lidar`          point cloud
   :class:`~tensorbay.sensor.sensor.Radar`          point cloud
   ===============================================  =================================

The corresponding class of sensor is :class:`~tensorbay.sensor.sensor.Sensor`.

*******
 frame
*******

Frame is the structural level next to the fusion segment.
Each frame contains multiple data collected from different sensors at the same time.

The corresponding class of frame is :class:`~tensorbay.dataset.frame.Frame`.

************************
 data in fusion dataset
************************

Each data inside a frame corresponds to a sensor.
And the data of the fusion dataset is the same as the data
(:ref:`ref <basic_concepts:data>`) of the dataset.
