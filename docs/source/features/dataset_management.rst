####################
 Dataset Management 
####################

This topic describes the key operations towards datasets, including:

- :ref:`features/dataset_management:Organize Dataset`
- :ref:`features/dataset_management:Upload Dataset`
- :ref:`features/dataset_management:Read Dataset`


******************
 Organize Dataset
******************

TensorBay SDK supports methods to organize local datasets
into uniform TensorBay :ref:`dataset structure <reference/dataset_structure:Dataset Structure>`.
The typical steps to organize a local dataset:

- First, write a :ref:`dataloader <reference/glossary:dataloader>`
  to load the whole local dataset into a :class:`~tensorbay.dataset.dataset.Dataset`
  instance.
- Second, write a :ref:`catalog <reference/dataset_structure:Catalog>`
  to store all the label meta information inside a dataset.

.. note::

   A catalog is needed only if there is label information inside the dataset.
   
Take the :ref:`Organization of BSTLD <examples/bstld:Organize Dataset>` as an example.


****************
 Upload Dataset
****************

There are two usages for the organized local dataset
(i.e. the initialized :class:`~tensorbay.dataset.dataset.Dataset` instance):

- Upload it to TensorBay.
- Use it from local.

This section mainly discusses the uploading operation.
There are plenty of benefits of uploading local datasets to TensorBay.

- **REUSE**: uploaded datasets can be reused without preprocessing again.
- **SHARING**: uploaded datasets can be shared the with your team or the community.
- **VISUALIZATION**: uploaded datasets can be visualized without coding.
- **VERSION CONTROL**: different versions of one dataset can be uploaded and controlled conveniently.

Take the :ref:`Uploading of BSTLD <examples/bstld:Upload Dataset>` as an example.

**************
 Read Dataset
**************

Two types of datasets can be read from TensorBay:

- Datasets uploaded by yourself as mentioned in :ref:`features/dataset_management:Upload Dataset`.
- Datasets uploaded by the community (check them on the `Open Datasets`_ platform.).

Take the :ref:`Reading of BSTLD <examples/bstld:Read Dataset>` as an example.

.. note::

   Before reading a dataset uploaded by the community, fork_ it first.

.. note::

   Visit `my datasets(or team datasets)`_ panel of `TensorBay`_ platform to check all
   datasets that can be read.

.. _fork: https://docs.graviti.cn/guide/opendataset/fork
.. _Open Datasets: https://www.graviti.cn/open-datasets
.. _my datasets(or team datasets): https://gas.graviti.cn/tensorbay/dataset-list
.. _TensorBay: https://gas.graviti.cn/tensorbay/
