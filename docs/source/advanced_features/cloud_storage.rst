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

TensorBay SDK supports a method to list a user's all previous configurations.

.. code:: python

    from tensorbay import GAS

    gas = GAS("<YOUR_ACCESSKEY>")
    gas.list_auth_storage_configs()


Create Authorized Storage Dataset
=================================

Create a dataset with authorized cloud storage:

.. code:: python

    dataset_client = gas.create_auth_dataset("dataset_name", "config_name", "path/to/dataset")

Import Cloud Files into Authorized Storage Dataset
==================================================

..
    There are two methods to import cloud files into an authorized storage dataset.

        - OUT-OF-THE-BOX: Import all files under a directory into a dataset.
        - CUSTOMIZED: Use AuthData to organize cloud files into a dataset.

Take the following cloud directory as an example::

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

..
    Out-of-the-box Method
    *********************

    Import all files in ``data/images`` directory into ``train`` segment.

    .. code:: python

       dataset_client.import_all_files("data/images", "train")

    Customized method support more features, such as uploading labels
    and selecting specific files.

    Customized Method
    *****************

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

    Files will be copied from raw directory to the authorized cloud storage dataset path,
    thus the storage space will be doubled on the cloud platform.
