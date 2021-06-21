##########################
 Getting Started with CLI
##########################

The TensorBay Command Line Interface is a tool to operate on datasets.
It supports Windows, Linux, and Mac platforms.

TensorBay CLI can:

 - Create and delete dataset.
 - List data, segments and datasets on TensorBay.
 - Upload data to TensorBay.

**************
 Installation
**************

To use TensorBay CLI, please install TensorBay SDK first.

.. code:: html

   pip3 install tensorbay

***************
 Configuration
***************

An accessKey_ is used for identification when using TensorBay to operate datasets.

.. _accesskey: https://gas.graviti.cn/tensorbay/developer

Set the accessKey into configuration:

.. code:: html

   gas auth [ACCESSKEY]

To show authentication information:

.. code:: html

   gas auth --get

******
 TBRN
******

TensorBay Resource Name(TBRN) uniquely defines the resource stored in TensorBay.
TBRN begins with ``tb:``. Default segment can be defined as ``""`` (empty string).
See more details in :ref:`TBRN <tensorbay_cli/tbrn:TensorBay Resource Name>`.
The following is the general format for TBRN:

.. code:: html

   tb:<dataset_name>[:<segment_name>][://<remote_path>]


*******
 Usage
*******

CLI: Create a Dataset
======================

.. code:: html

   gas dataset tb:<dataset_name>


CLI: List Dataset Names
========================

.. code:: html

   gas dataset


CLI: Create a Draft
====================

.. code:: html

   gas draft tb:<dataset_name> [-t <title>]


CLI: List Drafts
=================

.. code:: html

   gas draft -l tb:<dataset_name>


CLI: Upload a File To the Dataset
==================================

.. code:: html

   gas cp <local_path> tb:<dataset_name>#<draft_number>:<segment_name>


CLI: Commit the Draft
======================

.. code:: html

   gas commit tb:<dataset_name>#<draft_number> [-m <message>]
