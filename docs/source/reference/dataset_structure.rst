###################
 Dataset Structure
###################

For ease of use, TensorBay defines a uniform dataset format.
In this topic, we explain the related concepts.
The TensorBay dataset format looks like::

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
      
*********
 dataset
*********

Dataset is the topmost concept in TensorBay dataset format.
Each dataset includes a catalog and a certain number of segments.

The corresponding class of dataset is :class:`~tensorbay.dataset.dataset.Dataset`.

*********
 catalog 
*********

Catalog is used for storing label meta information.
It collects all the labels corresponding to a dataset.
There could be one or several subcatalogs (:ref:`reference/label_format:Label Format`)
under one catalog, each of which only stores label meta information of one label type.

For example, there is only one subcatalog ("BOX3D") in the catalog of dataset `Neolix OD`_.

.. _Neolix OD: https://www.graviti.cn/open-datasets/NeolixOD

.. literalinclude:: ../../tensorbay/opendataset/NeolixOD/catalog.json
   :language: json
   :name: NeolixOD-catalog

Note that catalog is not needed if there is no label information in a dataset.

*********
 segment
*********

There may be several parts in a dataset.
In TensorBay format, each part of the dataset is stored in one segment.
For example, all training samples of a dataset can be organized in a segment named "train".

The corresponding class of segment is :class:`~tensorbay.dataset.segment.Segment`.

******
 data
******

Data is the structural level next to segment.
One data contains one dataset sample and its related labels,
as well as any other information such as timestamp.

The corresponding class of data is :class:`~tensorbay.dataset.data.Data`.
