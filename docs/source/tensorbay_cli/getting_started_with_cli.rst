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

.. code:: console

   $ pip3 install tensorbay

******
 TBRN
******

TensorBay Resource Name(TBRN) uniquely defines the data stored in TensorBay.
TBRN begins with ``tb:``. Default segment can be defined as ``""`` (empty string).
The following is the general format for TBRN:

.. code:: console

   tb:[dataset_name]:[segment_name]://[remote_path]

***************
 Configuration
***************

Use the command below to configure the accessKey.

.. code:: console

   $ gas config [accessKey]

AccessKey_ is used for identification when using TensorBay to operate on dataset.

.. _accesskey: https://gas.graviti.cn/tensorbay/developer

Set the accessKey into configuration:

.. code:: console

   $ gas config Accesskey-*****

To show configuration information:

.. code:: console

   $ gas config
