################################
 Getting started with TensorBay
################################

**************
 Installation
**************

To install TensorBay SDK and CLI by **pip**, run the following command:

.. code:: console

   $ pip3 install tensorbay

To verify the SDK and CLI version, run the following command:

.. code:: console

   $ gas --version
   0.0.1


**************
 Registration
**************

Before using TensorBay SDK, please finish the following registration steps:

- Please visit `Graviti AI Service(GAS)`_ to sign up.
- Please visit `this page <https://gas.graviti.cn/access-key>`_ to get an AccessKey.

.. _graviti ai service(gas): https://www.graviti.cn/tensorBay

.. note::
   An AccessKey is needed to authenticate identity when using TensorBay via SDK or CLI.


*******
 Usage
*******

Authorize a Client Object
=========================

.. code:: python

   from tensorbay import GAS

   gas = GAS("<YOUR_ACCESSKEY>")

See :ref:`this page <tensorbay_cli/getting_start_with_CLI:Config>` for details
about authenticating identity via CLI.

Create a Dataset 
================

.. code:: python
   
   gas.create_dataset("DatasetName")

List Dataset Names
==================

.. code:: python

   dataset_list = list(gas.list_dataset_names())

Upload Images to the Dataset
============================

.. code:: python

   # Organize the local dataset by the "Dataset" class before uploading.
   from tensorbay.dataset import Data, Dataset

   dataset = Dataset("DatasetName")

   # TensorBay uses "segment" to separate different parts in a dataset.
   segment = dataset.create_segment()

   segment.append(Data("0000001.jpg"))
   segment.append(Data("0000002.jpg"))

   gas.upload_dataset(dataset)

Read Images from the Dataset
============================

.. code:: python

   from PIL import Image
   from tensorbay.dataset import Segment

   dataset_client = gas.get_dataset("DatasetName")

   segment = Segment("", dataset_client)

   for data in segment:
       with data.open() as fp:
           image = Image(fp)
           width, height = image.size
           image.show()

Delete the Dataset
==================

.. code:: python

   gas.delete_dataset("DatasetName")
