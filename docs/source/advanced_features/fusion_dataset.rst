..
 Copyright 2021 Graviti. Licensed under MIT License.
 
################
 Fusion Dataset
################

Fusion dataset represents datasets with data collected from multiple sensors.
Typical examples of fusion dataset are some autonomous driving datasets, such as `nuScenes`_ and `KITTI-tracking`_.

.. _nuScenes: https://gas.graviti.com/dataset/motional/nuScenes
.. _KITTI-tracking: https://gas.graviti.com/dataset/graviti/KITTITracking


Fusion dataset is one of the topmost concept in TensorBay format.
Each fusion dataset includes a catalog and a certain number of fusion segments.

The corresponding class of fusion dataset is :class:`~tensorbay.dataset.dataset.FusionDataset`.

**************************
 fusion dataset format
**************************

The uniform fusion dataset format in TensorBay is defined as follows::

   fusion dataset
   ├── notes
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

*******
 notes
*******

The notes of the fusion dataset is the same as the 
:ref:`notes <reference/dataset_structure:notes>` of the dataset.

****************************************
 catalog & subcatalog in fusion dataset
****************************************

The catalog of the fusion dataset is the same as the 
:ref:`catalog <reference/dataset_structure:catalog>` of the dataset.

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
And the data of the fusion dataset is the same as the 
:ref:`data <reference/dataset_structure:data>` of the dataset.

*********
 example 
*********

To learn more about fusion dataset, please read example of :doc:`/quick_start/examples/CADC`
