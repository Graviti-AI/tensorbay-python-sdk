##########
 Glossary
##########

accesskey
=========

An accesskey is an access credential for identification when using TensorBay to operate on your dataset.

To obtain an accesskey, log in to `Graviti AI Service(GAS)`_ and
visit the `developer page <https://gas.graviti.cn/tensorbay/developer>`_ to create one.

.. _graviti ai service(gas): https://www.graviti.cn/tensorBay

For the usage of accesskey via Tensorbay SDK or CLI,
please see :ref:`SDK authorization <quick_start/getting_started_with_tensorbay:Authorize a Client Object>`
or :ref:`CLI configration <tensorbay_cli/getting_started_with_cli:Configuration>`.

dataset
=======

A uniform dataset format defined by TensorBay,
which only contains one type of data collected from one sensor or without sensor information.
According to the time continuity of data inside the dataset, a dataset can be a discontinuous dataset or a continuous dataset.
:ref:`Notes <reference/dataset_structure:notes>` can be used to specify whether a dataset is continuous.

The corresponding class of dataset is :class:`~tensorbay.dataset.dataset.Dataset`.

See :ref:`reference/dataset_structure:Dataset Structure` for more details.

fusion dataset
==============

A uniform dataset format defined by Tensorbay,
which contains data collected from multiple sensors.

According to the time continuity of data inside the dataset, a fusion dataset can be a discontinuous fusion dataset or a continuous fusion dataset.
:ref:`Notes <reference/dataset_structure:notes>` can be used to specify whether a fusion dataset is continuous.

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

Here are some dataloader examples of datasets with different label types and continuity(:numref:`Table. %s <dataloaders_table>`).

.. _dataloaders_table:

.. table:: Dataloaders
   :align: center
   :widths: auto

   ================================  =============================================================================
    Dataloaders                       Description
   ================================  =============================================================================
   `LISA Traffic Light Dataloader`_  | This example is the dataloader of `LISA Traffic Light Dataset`_,
                                     | which is a continuous dataset with :ref:`reference/label_format:Box2D` label.
   `Dogs vs Cats Dataloader`_        | This example is the dataloader of `Dogs vs Cats Dataset`_,
                                     | which is a dataset with :ref:`reference/label_format:Classification` label.
   `BSTLD Dataloader`_               | This example is the dataloader of `BSTLD Dataset`_,
                                     | which is a dataset with :ref:`reference/label_format:Box2D` label.
   `Neolix OD Dataloader`_           | This example is the dataloader of `Neolix OD Dataset`_,
                                     | which is a dataset with :ref:`reference/label_format:Box3D` label.
   `Leeds Sports Pose Daraloader`_   | This example is the dataloader of `Leeds Sports Pose Dataset`_,
                                     | which is a dataset with :ref:`reference/label_format:Keypoints2D` label.
   ================================  =============================================================================

.. _Dogs vs Cats Dataloader: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/DogsVsCats/loader.py
.. _Dogs vs Cats Dataset: https://gas.graviti.cn/dataset/data-decorators/DogsVsCats
.. _BSTLD Dataloader: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/BSTLD/loader.py
.. _BSTLD Dataset: https://gas.graviti.cn/dataset/data-decorators/BSTLD
.. _Neolix OD Dataloader: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/NeolixOD/loader.py
.. _Neolix OD Dataset: https://gas.graviti.cn/dataset/graviti-open-dataset/NeolixOD
.. _Leeds Sports Pose Daraloader: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/LeedsSportsPose/loader.py
.. _Leeds Sports Pose Dataset: https://gas.graviti.cn/dataset/data-decorators/LeedsSportsPose
.. _LISA Traffic Light Dataloader: https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/tensorbay/opendataset/LISATrafficLight/loader.py
.. _LISA Traffic Light Dataset: https://gas.graviti.cn/dataset/hello-dataset/LISATrafficLight

.. note::

  The name of the dataloader function is a unique indentification of the dataset.
  It is in upper camel case and is generally obtained by removing special characters from the dataset name.

  Take `Dogs vs Cats`_ dataset as an example,
  the name of its dataloader function is :meth:`~tensorbay.opendataset.DogsVsCats.loader.DogsVsCats`.

  .. _dogs vs cats: https://gas.graviti.cn/dataset/data-decorators/DogsVsCats

See more dataloader examples in :ref:`api/opendataset/opendataset_module:tensorbay.opendataset`.

TBRN
====

TBRN is the abbreviation for TensorBay Resource Name, which represents the data or a collection of data stored in TensorBay uniquely.

Note that TBRN is only used in :ref:`CLI<tensorbay_cli/getting_started_with_cli:Getting Started with CLI>`.

TBRN begins with ``tb:``, followed by the dataset name, the segment name and the file name.

The following is the general format for TBRN:

.. code::

    tb:[dataset_name]:[segment_name]://[remote_path]

Suppose there is an image ``000000.jpg`` under the default segment of a dataset named ``example``,
then the TBRN of this image should be:

.. code::

    tb:example:://000000.jpg

.. note::

   Default segment is defined as ``""`` (empty string).


commit
======

Similar with Git, a commit is a version of a dataset,
which contains the changes compared with the former commit.
A certain commit of a dataset can be accessed by passing the corresponding commit ID.

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
Under these circumstances, create a draft, edit the dataset and commit the draft.
