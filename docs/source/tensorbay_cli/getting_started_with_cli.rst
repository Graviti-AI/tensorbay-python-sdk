##########################
 Getting Started with CLI
##########################

The TensorBay Command Line Interface is a tool to operate on your datasets.
It supports Windows, Linux, and Mac platforms.

You can use TensorBay CLI to:

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

Use the command below to configure the accessKey and URL(optional).

.. code:: console

   $ gas config [accessKey] [url]

AccessKey_ is used for identification when using TensorBay to operate on your dataset.
The default url is "https://gas.graviti.cn/".

.. _accesskey: https://gas.graviti.cn/access-key

You can set the accessKey and URL into configuration:

.. code:: console

   $ gas config Accesskey-***** https://gas.graviti.cn/

To show configuration information:

.. code:: console

   $ gas config

You can also log in with specified accessKey and URL to interact with TensorBay.

.. code:: console

   $ gas -u [url] -k [accessKey] [command] [args]

For example, to list all datasets with accessKey and URL:

.. code:: console

   $ gas -u https://gas.uat.graviti.cn/ -k Accesskey-***** ls
