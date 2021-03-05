##############
 Read Dataset
##############

TensorBay SDK provides a method to read dataset from TensorBay, and there are two circumstances:

- Read datasets uploaded by yourself.
- Read datasets uploaded by community.

Note that in the second circumstance, two steps should be done first:

- obtain_
- fork_

.. _fork: https://docs.graviti.cn/guide/opendataset/fork

.. _obtain: https://docs.graviti.cn/guide/opendataset/get

Pass the correct dataset name to a **GAS client**, and you will get a **dataset client**.
You can operate the dataset via this client.

.. code:: python

   from tensorbay import GAS

   ACCESS_KEY = "Accesskey-*****"
   gas = GAS(ACCESS_KEY)
   dataset_client = gas.get_dataset("dataset_name")

If you are not sure about the dataset name, you can visit our `Graviti AI Service(GAS)`_ to verify.

.. _graviti ai service(gas): https://www.graviti.cn/tensorBay

See :ref:`examples <examples:Examples>` for further details about using datasets.
