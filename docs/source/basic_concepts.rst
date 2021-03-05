################
 Basic Concepts
################

In this topic, we explain the related concepts of the dataset structure in TensorBay format.
TensorBay divides all datasets into two types based on the number of the sensors in a dataset:

- **dataset**
- **fusion dataset**

To facilitate the understanding,
we use dataset (plain) to refer to the overall concept of dataset,
and use **dataset** (boldface) and **fusion dataset** (boldface) to refer to
the concrete dataset types TensorBay defines.
Thus, we can say that dataset includes **dataset** type and **fusion dataset** type.

:numref:`Table. %s <corresponding_classes>` lists the concepts and their corresponding classes.

.. _corresponding_classes:

.. table:: concepts and their corresponding classes
   :align: center
   :width: 70%

   ==================  ============================================================================
   Concepts            Classes
   ==================  ============================================================================
   **dataset**         :class:`~tensorbay.dataset.dataset.Dataset`        
   **fusion dataset**  :class:`~tensorbay.dataset.dataset.FusionDataset`
   **segment**         :class:`~tensorbay.dataset.segment.Segment`
   **fusion segment**  :class:`~tensorbay.dataset.segment.FusionSegment`
   **frame**           :class:`~tensorbay.dataset.frame.Frame`
   **data**            :class:`~tensorbay.dataset.data.Data`
   **sensor**          :class:`~tensorbay.sensor.sensor.Sensor`
   ==================  ============================================================================


**************************
 Dataset Related Concepts
**************************

**Dataset** represents the most common datasets such as `MNIST`_ and `THUCNews`_.
It is made up of data collected from only one sensor or data without sensor information.
See :ref:`this part <basic_concepts:Fusion Dataset Related Concepts>` for the comparison between
**dataset** and **fusion dataset**.

The structure of a **dataset** looks like::

   dataset
   ├── catalog
   │   ├── subcatalog
   │   ├── subcatalog
   │   └── ...
   ├── segment
   │   ├── data
   │   ├── data
   │   └── ...
   ├── segment
   │   ├── data
   │   ├── data
   │   └── ...
   └── ...
      
      
      

.. _MNIST: https://www.graviti.cn/open-datasets/MNIST
.. _THUCNews: https://www.graviti.cn/open-datasets/THUCNews

dataset
=======

**Dataset** is one of the dataset types that TensorBay defines.
A **dataset** includes all the data, label and any other information of a dataset.

The corresponding class of **dataset** is :class:`~tensorbay.dataset.dataset.Dataset`.

Structurally, a **dataset** contains a **catalog** and a certain number of **segments**.

catalog & subcatalog
====================

**Catalog** stores the label meta information.
It collects all the labels occurred in all samples of a dataset.

There could be one or several **subcatalogs** (:ref:`supported_label_types:supported label types`)
under one **catalog**,
each of which only stores label meta information of one label type.

Code block below is the **catalog** of dataset `Neolix OD`_,
and there is only one **subcatalog** "BOX3D".

.. _Neolix OD: https://www.graviti.cn/open-datasets/NeolixOD

.. literalinclude:: ../../tensorbay/opendataset/NeolixOD/catalog.json
   :language: json
   :name: NeolixOD-catalog
   :linenos:

segment
=======

**Segment** is the structural level second to **dataset**.
Each **segment** contains a certain number of **data**.
For example, all training samples of a **dataset** can be organized in a **segment** named "train".

The corresponding class of **segment** is :class:`~tensorbay.dataset.segment.Segment`.

data
====

**Data** is the structural level next to **segment**.
One **data** contains one dataset sample and its related labels
and any other information such as timestamp.

The corresponding class of **data** is :class:`~tensorbay.dataset.data.Data`.

********************************
 Fusion Dataset Related Concepts
********************************

Different with **dataset**,
**fusion dataset** represents datasets with data collected from multiple sensors.
Typical examples of **fusion dataset** are a group of autonomous driving datasets,
such as `nuScenes`_ and `KITTI-tracking`_.

The structure of a **fusion dataset** looks like::

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

.. _nuScenes: https://www.graviti.cn/open-datasets/nuScenes
.. _KITTI-tracking: https://www.graviti.cn/open-datasets/KITTItracking

fusion dataset
==============

**Fusion dataset** is one of the dataset types that TensorBay defines.

It is made up of data collected from multiple sensors
and contains all the frames, labels, sensors and any other information of a fusion dataset.

The corresponding class of **fusion dataset** is :class:`~tensorbay.dataset.dataset.FusionDataset`.

Structurally,
a **fusion dataset** contains a **catalog** and a certain number of **fusion segments**.

fusion segment
==============

**Fusion segment** is the structural level second to **fusion dataset**.
Each **fusion segment** contains a certain number of **frames**.
Besides, a **fusion segment** contains multiple **sensors**,
from which the data inside the fusion segment are collected.

The corresponding class of **fusion segment** is :class:`~tensorbay.dataset.segment.FusionSegment`.


sensor
======

**Sensor** represents the device that collects the data inside the fusion segment.

Currently, we support four sensor types.(:numref:`Table. %s <supported_sensors>`)

.. _supported_sensors:

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

The corresponding class of **sensor** is :class:`~tensorbay.sensor.sensor.Sensor`.

frame
=====

**Frame** is the structural level next to **fusion segment**.
Each **frame** contains multiple **data** collected from different sensors at the same time.

The corresponding class of **frame** is :class:`~tensorbay.dataset.frame.Frame`.

data in fusion dataset
======================

Each **data** inside a **frame** corresponds to a **sensor**.
And the **data** in **fusion dataset** is the same as the **data** in **dataset**.
