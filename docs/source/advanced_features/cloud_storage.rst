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

.. important::

    The directory ``path/to/dataset`` should be empty when create an authorized storage Fusion Dataset.
