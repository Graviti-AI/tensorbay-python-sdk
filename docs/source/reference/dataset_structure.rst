###################
 Dataset Structure
###################

For ease of use, TensorBay defines a uniform dataset format.
This topic explains the related concepts.
The TensorBay dataset format looks like::

   dataset
   ├── notes
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

*******
 notes
*******

Notes contains the basic information of a dataset, including

- the time continuity of the data inside the dataset
- the fields of bin point cloud files inside the dataset

The corresponding class of notes is :class:`~tensorbay.dataset.dataset.Notes`.

*********
 catalog 
*********

Catalog is used for storing label meta information.
It collects all the labels corresponding to a dataset.
There could be one or several subcatalogs (:ref:`reference/label_format:Label Format`)
under one catalog. Each Subcatalog only stores label meta information of one label type,
including whether the corresponding annotation has tracking information.

Here are some catalog examples of datasets with different label types and a dataset with tracking annotations(:numref:`Table. %s <catalogs_table>`).

.. _catalogs_table:

.. table:: Catalogs
   :align: center
   :widths: auto

   =============================  =============================================================================
    Catalogs                       Description
   =============================  =============================================================================
   `elpv Catalog`_                | This example is the catalog of `elpv Dataset`_,
                                  | which is a dataset with :ref:`reference/label_format:Classification` label.
   `BSTLD Catalog`_               | This example is the catalog of `BSTLD Dataset`_,
                                  | which is a dataset with :ref:`reference/label_format:Box2D` label.
   `Neolix OD Catalog`_           | This example is the catalog of `Neolix OD Dataset`_,
                                  | which is a dataset with :ref:`reference/label_format:Box3D` label.
   `Leeds Sports Pose Catalog`_   | This example is the catalog of `Leeds Sports Pose Dataset`_,
                                  | which is a dataset with :ref:`reference/label_format:Keypoints2D` label.
   `NightOwls Catalog`_           | This example is the catalog of `NightOwls Dataset`_,
                                  | which is a dataset with tracking :ref:`reference/label_format:Box2D` label.
   =============================  =============================================================================

.. _elpv Catalog: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/Elpv/catalog.json
.. _elpv Dataset: https://gas.graviti.cn/dataset/data-decorators/Elpv
.. _BSTLD Catalog: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/BSTLD/catalog.json
.. _BSTLD Dataset: https://gas.graviti.cn/dataset/data-decorators/BSTLD
.. _Neolix OD Catalog: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/NeolixOD/catalog.json
.. _Neolix OD Dataset: https://gas.graviti.cn/dataset/graviti-open-dataset/NeolixOD
.. _Leeds Sports Pose Catalog: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/LeedsSportsPose/catalog.json
.. _Leeds Sports Pose Dataset: https://gas.graviti.cn/dataset/data-decorators/LeedsSportsPose
.. _NightOwls Catalog: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/NightOwls/catalog.json
.. _NightOwls Dataset: https://gas.graviti.cn/dataset/hello-dataset/NightOwls

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
