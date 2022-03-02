..
 Copyright 2021 Graviti. Licensed under MIT License.
 
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
please see :ref:`SDK authorization <quick_start/getting_started_with_tensorbay:Authorize a Client Instance>`
or :ref:`CLI configration <tensorbay_cli/getting_started_with_cli:Authentication>`.

basehead
========
The basehead is the string for recording the two relative versions(commits or drafts) in the
format of "base...head".

The basehead param is comprised of two parts: base and head. Both must be :ref:`reference/glossary:revision`
or draft number in dataset. The terms "head" and "base" are used as they normally are in Git.

The head is the version which changes are on.
The base is the version of which these changes are based.

branch
======

Similar to git, a branch is a lightweight pointer to one of the commits.

Every time a :ref:`reference/glossary:commit` is submitted,
the main branch pointer moves forward automatically to the latest commit.

commit
======

Similar with Git, a commit is a version of a dataset,
which contains the changes compared with the former commit.

Each commit has a unique commit ID, which is a uuid in a 36-byte hexadecimal string.
A certain commit of a dataset can be accessed by passing the corresponding commit ID
or other forms of :ref:`reference/glossary:revision`.

A commit is readable, but is not writable.
Thus, only read operations such as getting catalog, files and labels are allowed.
To change a dataset, please create a new commit.
See :ref:`reference/glossary:draft` for details.

On the other hand,
"commit" also represents the action to save the changes inside a :ref:`reference/glossary:draft` into a commit.

continuity
==========

Continuity is a characteristic to describe the data within a :ref:`reference/glossary:dataset` or a :ref:`reference/glossary:fusion dataset`.

A dataset is continuous means the data in each segment of the dataset is collected over a continuous period of time
and the collection order is indicated by the data paths or frame indexes.

The continuity can be set in :ref:`reference/dataset_structure:notes`.

Only continuous datasets can have :ref:`reference/glossary:tracking` labels.

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

   ================================  ============================================================================================
    Dataloaders                       Description
   ================================  ============================================================================================
   `LISA Traffic Light Dataloader`_  | This example is the dataloader of `LISA Traffic Light Dataset`_,
                                     | which is a continuous dataset with :doc:`/reference/label_format/Box2D` label.
   `Dogs vs Cats Dataloader`_        | This example is the dataloader of `Dogs vs Cats Dataset`_,
                                     | which is a dataset with :doc:`/reference/label_format/Classification` label.
   `BSTLD Dataloader`_               | This example is the dataloader of `BSTLD Dataset`_,
                                     | which is a dataset with :doc:`/reference/label_format/Box2D` label.
   `Neolix OD Dataloader`_           | This example is the dataloader of `Neolix OD Dataset`_,
                                     | which is a dataset with :doc:`/reference/label_format/Box3D` label.
   `Leeds Sports Pose Daraloader`_   | This example is the dataloader of `Leeds Sports Pose Dataset`_,
                                     | which is a dataset with :doc:`/reference/label_format/Keypoints2D` label.
   ================================  ============================================================================================

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

See more dataloader examples in :ref:`reference/api/opendataset:tensorbay.opendataset`.

dataset
=======

A uniform dataset format defined by TensorBay,
which only contains one type of data collected from one sensor or without sensor information.
According to the time continuity of data inside the dataset, a dataset can be a discontinuous dataset or a continuous dataset.
:ref:`Notes <reference/dataset_structure:notes>` can be used to specify whether a dataset is continuous.

The corresponding class of dataset is :class:`~tensorbay.dataset.dataset.Dataset`.

See :doc:`/reference/dataset_structure` for more details.

diff
====

TensorBay supports showing the status difference of the relative
resource between commits or drafts in the form of diff.

draft
=====

Similar with Git, a draft is a workspace in which changing the dataset is allowed.

A draft is created based on a :ref:`reference/glossary:branch`,
and the changes inside it will be made into a commit.

There are scenarios when modifications of a dataset are required,
such as correcting errors, enlarging dataset, adding more types of labels, etc.
Under these circumstances, create a draft, edit the dataset and commit the draft.

fusion dataset
==============

A uniform dataset format defined by Tensorbay,
which contains data collected from multiple sensors.

According to the time continuity of data inside the dataset, a fusion dataset can be a discontinuous fusion dataset or a continuous fusion dataset.
:ref:`Notes <reference/dataset_structure:notes>` can be used to specify whether a fusion dataset is continuous.

The corresponding class of fusion dataset is :class:`~tensorbay.dataset.dataset.FusionDataset`.

See :doc:`/advanced_features/fusion_dataset` for more details.

revision
========

Similar to Git, a revision is a reference to a single :ref:`reference/glossary:commit`.
And many methods in TensorBay SDK take revision as an argument.

Currently, a revision can be in the following forms:

1. A full :ref:`reference/glossary:commit` ID.
2. A :ref:`reference/glossary:tag`.
3. A :ref:`reference/glossary:branch`.

tag
===

TensorBay SDK has the ability to tag the specific :ref:`reference/glossary:commit` in a dataset's history
as being important. Typically, people use this functionality to mark release points (v1.0, v2.0 and so on).

TBRN
====

TBRN is the abbreviation for TensorBay Resource Name, which represents the data or a collection of data stored in TensorBay uniquely.

Note that TBRN is only used in :doc:`CLI</tensorbay_cli/getting_started_with_cli>`.

TBRN begins with ``tb:``, followed by the dataset name, the segment name and the file name.

The following is the general format for TBRN:

.. code::

    tb:[dataset_name]:[segment_name]://[remote_path]

Suppose there is an image ``000000.jpg`` under the ``train`` segment of a dataset named ``example``,
then the TBRN of this image should be:

.. code::

    tb:example:train://000000.jpg

tracking
========

Tracking is a characteristic to describe the labels within a :ref:`reference/glossary:dataset` or a :ref:`reference/glossary:fusion dataset`.

The labels of a dataset are tracking means the labels contain tracking information, such as tracking ID, which is used for tracking tasks.

Tracking characteristic is stored in :ref:`reference/dataset_structure:catalog`,
please see :doc:`/reference/label_format/index` for more details.
