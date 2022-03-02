..
 Copyright 2021 Graviti. Licensed under MIT License.
 
##########################
 Getting Started with CLI
##########################

The TensorBay Command Line Interface is a tool to operate on datasets.
It supports Windows, Linux, and Mac platforms.

TensorBay CLI supports:

 - list, create and delete operations for dataset, segment and data.
 - uploading data to TensorBay.
 - version control operations with branch, tag, draft and commit.
 - showing commit logs of dataset on TensorBay.

**************
 Installation
**************

To use TensorBay CLI, please install TensorBay SDK first.

.. code:: html

   $ pip3 install tensorbay

****************
 Authentication
****************

An accessKey_ is used for identification when using TensorBay to operate datasets.

.. _accesskey: https://gas.graviti.cn/tensorbay/developer

Set the accessKey into configuration:

.. code:: html

   $ gas auth [ACCESSKEY]

To show authentication information:

.. code:: html

   $ gas auth --get

******
 TBRN
******

TensorBay Resource Name(TBRN) uniquely defines the resource stored in TensorBay.
TBRN begins with ``tb:``.
See more details in :doc:`TBRN </tensorbay_cli/tbrn>`.
The following is the general format for TBRN:

.. code:: html

   tb:<dataset_name>[:<segment_name>][://<remote_path>]


*******
 Usage
*******

CLI: Create a Dataset
======================

.. code:: html

   $ gas dataset tb:<dataset_name>


CLI: List Dataset Names
========================

.. code:: html

   $ gas dataset


CLI: Create a Draft
====================

.. code:: html

   $ gas draft tb:<dataset_name> [-m <title>]


CLI: List Drafts
=================

.. code:: html

   $ gas draft -l tb:<dataset_name>


CLI: Upload a File To the Dataset
==================================

.. code:: html

   $ gas cp <local_path> tb:<dataset_name>#<draft_number>:<segment_name>


CLI: Commit the Draft
======================

.. code:: html

   $ gas commit tb:<dataset_name>#<draft_number> [-m <title>]

*********
 Profile
*********

For users with multiple TensorBay accounts or different workspaces,
CLI provides profiles to easily authenticate and use different accessKeys.

Set the accessKey into the specific profile, and
show the specific profile's authentication information:

.. code:: html

   $ gas -p <profile_name> auth [ACCESSKEY]
   $ gas -p <profile_name> auth -g

After authentication, the profiles can be used to execute other commands:

.. code:: html

   $ gas -p <profile_name> <command>

For example, list all the datasets with the given profile's accessKey:

.. code:: html

   $ gas -p <profile_name> ls

For users who want to use a temporary accessKey,
CLI provides ``-k`` option to override the authentication:

.. code:: html

   $ gas -k <Accesskey> <command>

For example, list all the datasets with the given accessKey:

.. code:: html

   $ gas -k <AccessKey> ls

