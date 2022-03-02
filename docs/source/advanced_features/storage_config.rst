..
 Copyright 2021 Graviti. Licensed under MIT License.
 
################
 Storage Config
################

TensorBay supports two storage config modes:

    - GRAVITI Storage Config: storage config provided by graviti.
    - Authorized Storage Config: storage config provided by userself.

************************
 GRAVITI Storage Config
************************
In graviti storage mode, the data is stored in graviti storage space on TensorBay.

***************************
 Authorized Storage Config
***************************

When using authorized storage config, datasets are stored on user's storage space and are only indexed to the TensorBay.
See `authorized storage instruction <https://docs.graviti.cn/guide/tensorbay/data/authorize>`_ for details about how to configure authorized storage on TensorBay.

TensorBay supports both authorize cloud storage and authorize local storage.

Authorized Cloud Storage
========================

TensorBay SDK supports following methods to configure authorized cloud storage.

    - :func:`~tensorbay.client.gas.GAS.create_oss_storage_config`
    - :func:`~tensorbay.client.gas.GAS.create_s3_storage_config`
    - :func:`~tensorbay.client.gas.GAS.create_azure_storage_config`

For example:

.. literalinclude:: ../../../docs/code/storage_config.py
   :language: python
   :start-after: """Create storage config"""
   :end-before: """"""

TensorBay SDK supports a method to list a user's all previous configurations.

.. code:: python

    gas.list_auth_storage_configs()


Create Authorized Storage Dataset
---------------------------------

Create a dataset with authorized cloud storage:

.. code:: python

    dataset_client = gas.create_dataset("<DATASET_NAME>", config_name="<CONFIG_NAME>")

Import Cloud Files into Authorized Storage Dataset
--------------------------------------------------

Take the following original cloud storage directory as an example::

   data/
   ├── images/
   │   ├── 00001.png
   │   ├── 00002.png
   │   └── ...
   ├── labels/
   │   ├── 00001.json
   │   ├── 00002.json
   │   └── ...
   └── ...

Get a cloud client.

.. literalinclude:: ../../../docs/code/storage_config.py
   :language: python
   :start-after: """Get cloud client"""
   :end-before: """"""

Import the AuthData from original cloud storage and load label file to an authorized storage dataset.

.. literalinclude:: ../../../docs/code/storage_config.py
   :language: python
   :start-after: """Import dataset from cloud platform to the authorized storage dataset"""
   :end-before: """"""

.. important::

    Files will be copied from original directory to the authorized storage dataset path,
    thus the storage space will be doubled.

.. note::

    Set the authorized storage dataset path the same as original cloud storage directory could speed up
    the import action. For example, set the config path of above dataset to ``data/images``.

Authorized Local Storage
========================

If you want to use TensorBay service and have the data stored locally at the same time,
TensorBay supports authorized local storage config.

Before creating the local storage config via :func:`~tensorbay.client.gas.GAS.create_local_storage_config`,
you need to start a local storage service. Please contact us on `TensorBay`_ for more information.

.. _TensorBay: https://www.graviti.cn/

.. literalinclude:: ../../../docs/code/storage_config.py
   :language: python
   :start-after: """Create local storage config"""
   :end-before: """"""

Then create an authorized local storage dataset with the config.

.. literalinclude:: ../../../docs/code/storage_config.py
   :language: python
   :start-after: """Create authorized local storage dataset"""
   :end-before: """"""

Other operations such as uploading data and reading data,
are the same as datasets created by default,
except that the uploaded data is stored under the local storage.
