####################
 Dataset Management 
####################

This topic describes the key operations towards your datasets, including:

- :ref:`features/dataset_management:Organize Dataset`
- :ref:`features/dataset_management:Upload Dataset`
- :ref:`features/dataset_management:Read Dataset`


******************
 Organize Dataset
******************

TensorBay SDK supports methods to organize your local datasets
into uniform TensorBay dataset strucutre
(:ref:`ref <reference/dataset_structure:Dataset Structure>`).
The typical steps to organize a local dataset:

- First, write a dataloader (:ref:`ref <reference/glossary:dataloader>`)
  to load the whole local dataset into a :class:`~tensorbay.dataset.dataset.Dataset`
  instance,
- Second, write a catalog (:ref:`ref <reference/dataset_structure:Catalog>`)
  to store all the label meta information inside a dataset.

.. note::

   A catalog is needed only if there is label information inside the dataset.

:ref:`This part <examples/bstld:Organize Dataset>` is an example for organizing a dataset.


****************
 Upload Dataset
****************

There are two usages for the organized local dataset
(i.e. the initialized :class:`~tensorbay.dataset.dataset.Dataset` instance):

- Upload it to TensorBay.
- Use it directly.

In this section, we mainly discuss the uploading operation.
See :ref:`this example <examples/read_dataset_class:Read "Dataset" class>`
for details about the latter usage.

There are plenty of benefits of uploading local datasets to TensorBay.

- Reuse: you can reuse your dataset without preprocessing again.
- Share: you can share them with your team or the community.
- Preview: you can preview your datasets without coding.
- Version control: you can upload different versions of one dataset and control them conveniently.


:ref:`This part <examples/bstld:Upload Dataset>` is an example for uploading a dataset.

**************
 Read Dataset
**************

There are two types of datasets you can read from TensorBay:

- Datasets uploaded by yourself as mentioned in :ref:`features/dataset_management:Upload Dataset`.
- Datasets uplaoded by the community (i.e. the `open datasets`_).

.. note::

   Two steps, obtain_ and fork_, should be done
   before reading datasets uploaded by the community.

.. note::

   You can visit our `Graviti AI Service(GAS)`_ platform to check the dataset details,
   such as dataset name, version information, etc.

:ref:`This part <examples/bstld:Read Dataset>` is an example for reading a dataset.

.. _fork: https://docs.graviti.cn/guide/opendataset/fork
.. _obtain: https://docs.graviti.cn/guide/opendataset/get
.. _open datasets: https://www.graviti.cn/open-datasets
.. _Graviti AI Service(GAS): https://www.graviti.cn/tensorBay
