###############
 Cloud Storage
###############

| All data on TensorBay are hosted on cloud.
| TensorBay supports two cloud storage modes:

    - DEFAULT CLOUD STORAGE: data are stored on TensorBay cloud
    - AUTHORIZED CLOUD STORAGE: data are stored on other providers' cloud

***********************
 Default Cloud Storage
***********************
| In default cloud storage mode, data are stored on TensorBay cloud.
| Create a dataset with default storage:

.. literalinclude:: ../../../docs/code/getting_started_with_tensorbay.py
      :language: python
      :start-after: """Create a Dataset"""
      :end-before: """"""

**************************
 Authorized Cloud Storage
**************************

| You can also upload data to your public cloud storage space.
| Now TensorBay support following cloud providers:

    - Aliyun OSS
    - Amazon S3
    - Azure Blob

Config
======

See `cloud storage instruction <https://docs.graviti.cn/guide/tensorbay/data/authorize>`_ for details about how to configure cloud storage on TensorBay.

TensorBay SDK supports following methods to configure cloud storage.

    - :func:`~tensorbay.client.gas.GAS.create_oss_storage_config`
    - :func:`~tensorbay.client.gas.GAS.create_s3_storage_config`
    - :func:`~tensorbay.client.gas.GAS.create_azure_storage_config`

For example:

.. literalinclude:: ../../../docs/code/cloud_storage.py
   :language: python
   :start-after: """Create storage config"""
   :end-before: """"""

TensorBay SDK supports a method to list a user's all previous configurations.

.. code:: python

    gas.list_auth_storage_configs()


Create Authorized Storage Dataset
=================================

Create a dataset with authorized cloud storage:

.. code:: python

    dataset_client = gas.create_dataset("dataset_name", config_name="config_name")

Import Cloud Files into Authorized Storage Dataset
==================================================

Take the following original cloud directory as an example::

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

.. literalinclude:: ../../../docs/code/cloud_storage.py
   :language: python
   :start-after: """Get cloud client"""
   :end-before: """"""

Import the AuthData from cloud platform and load label file to an authorized storage dataset.

.. literalinclude:: ../../../docs/code/cloud_storage.py
   :language: python
   :start-after: """Import dataset from cloud platform to the authorized storage dataset"""
   :end-before: """"""

.. important::

    Files will be copied from original directory to the authorized cloud storage dataset path,
    thus the storage space will be doubled on the cloud platform.

.. note::

    Set the authorized cloud storage dataset path the same as original directory could speed up
    the import action. For example, set the config path of above dataset to ``data/images``.
