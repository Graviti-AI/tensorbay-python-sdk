
################
 Manage Dataset
################

This topic describes the basic operations towards your dataset, including:

- Create dataset
- Upload dataset to TensorBay
- Read dataset from TensorBay

****************
 Create Dataset
****************

To create a dataset,
you need to write a **dataloader** and a **catalog** (:ref:`basic_concepts:catalog & subcatalog`),
**catalog** is needed only if there is label information inside the dataset.

A **dataloader** is a function to read the original dataset files into a **dataset**.

See :ref:`examples <examples:Examples>` for further details about creating datasets.

****************
 Upload Dataset
****************

Once you write your own **dataloader** and read the local dataset files into a dataset,
you can upload it to TensorBay to use it online or to share with the community.

.. code:: python

   from tensorbay import GAS

   ACCESS_KEY = "Accesskey-*****"
   gas = GAS(ACCESS_KEY)

   gas.create_dataset(dataset.name)
   dataset_client = gas.upload_dataset(dataset)
   dataset_client.commit()

Remember to execute the :ref:`commit <features/version_control:Commit>` step after uploading.
If needed, you can re-upload and commit again.
Please see :ref:`version control <features/version_control:Version Control>` for more details.

.. note::

   The commit operation can also be done on our GAS_ Platform.

.. _gas: https://www.graviti.cn/tensorBay


**************
 Read Dataset
**************

Once the created dataset is uploaded to TensorBay, you can read it through TensorBay SDK.

Also, you read the datasets uploaded by the community, but two steps should be done first:

- obtain_
- fork_

.. _fork: https://docs.graviti.cn/guide/opendataset/fork

.. _obtain: https://docs.graviti.cn/guide/opendataset/get

After the preparation, pass the correct dataset name to a **GAS client**, and you will get a **dataset client**.
You can operate the dataset via this client.

.. code:: python

   from tensorbay import GAS

   ACCESS_KEY = "Accesskey-*****"
   gas = GAS(ACCESS_KEY)
   dataset_client = gas.get_dataset("dataset_name")

If you are not sure about the dataset name, you can visit our `Graviti AI Service(GAS)`_ to verify.

.. _graviti ai service(gas): https://www.graviti.cn/tensorBay

See :ref:`examples <examples:Examples>` for further details about using datasets.
