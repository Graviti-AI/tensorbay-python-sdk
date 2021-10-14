####################
 Dataset Management
####################

This topic describes dataset management, including:

- :ref:`features/dataset_management:Organize Dataset`
- :ref:`features/dataset_management:Upload Dataset`
- :ref:`features/dataset_management:Read Dataset`
- :ref:`features/dataset_management:Update Dataset`
- :ref:`features/dataset_management:Move and Copy`
- :ref:`features/dataset_management:Merge Datasets`
- :ref:`features/dataset_management:Get Label Statistics`


******************
 Organize Dataset
******************

TensorBay SDK supports methods to organize local datasets
into uniform TensorBay :ref:`dataset structure <reference/dataset_structure:Dataset Structure>`.
The typical steps to organize a local dataset:

- First, write a catalog (:ref:`ref <reference/dataset_structure:Catalog>`)
  to store all the label schema information inside a dataset.
- Second, write a dataloader (:ref:`ref <reference/glossary:dataloader>`)
  to load the whole local dataset into a :class:`~tensorbay.dataset.dataset.Dataset`
  instance.

.. note::

   A catalog is needed only if there is label information inside the dataset.

Take the :ref:`Organization of BSTLD <examples/bstld:Organize Dataset>` as an example.


****************
 Upload Dataset
****************

For an organized local dataset (i.e. the initialized :class:`~tensorbay.dataset.dataset.Dataset`
instance), users can:

- Upload it to TensorBay.
- Read it directly.

This section mainly discusses the uploading operation.
There are plenty of benefits of uploading local datasets to TensorBay.

- **REUSE**: uploaded datasets can be reused without preprocessing again.
- **SHARING**: uploaded datasets can be shared the with your team or the community.
- **VISUALIZATION**: uploaded datasets can be visualized without coding.
- **VERSION CONTROL**: different versions of one dataset can be uploaded and controlled conveniently.

.. note::

   During uploading dataset or data, if the remote path of the data is the same as another data under the same segment,
   the old data will be replaced.

Take the :ref:`Upload Dataset of BSTLD <examples/bstld:Upload Dataset>` as an example.

**************
 Read Dataset
**************

Two types of datasets can be read from TensorBay:

- Datasets uploaded by yourself as mentioned in :ref:`features/dataset_management:Upload Dataset`.
- Datasets uploaded by the shared `Open Datasets`_ platform.

.. note::

   Before reading a dataset uploaded by the community, fork_ it first.

.. note::

   Visit `my datasets(or team datasets)`_ panel of `TensorBay`_ platform to check all
   datasets that can be read.

.. _fork: https://docs.graviti.cn/guide/opendataset/fork
.. _Open Datasets: https://gas.graviti.cn/open-datasets
.. _my datasets(or team datasets): https://gas.graviti.cn/tensorbay/dataset-list
.. _TensorBay: https://gas.graviti.cn/tensorbay/

Take the :ref:`Read Dataset of BSTLD <examples/bstld:Read Dataset>` as an example.

****************
 Update Dataset
****************

Since TensorBay supports version control, users can update dataset meta, notes, data and labels to a new commit of a dataset.
Thus, different versions of data and labels can coexist in one dataset, which greatly facilitates the datasets' maintenance.

Please see :ref:`Update dataset<examples/update_dataset:Update Dataset>` example for more details.

***************
 Move and Copy
***************

TensorBay supports four methods to copy or move data in datasets:

- copy segments
- copy data
- move segments
- move data

Copy is supported within a dataset or between datasets.

Moving is only supported within one dataset.

.. note::

   The target dataset of copying and moving must be in :ref:`reference/glossary:draft` status.

Please see :ref:`Move and copy<examples/move_and_copy:Move And Copy>` example for more details.

****************
 Merge Datasets
****************

Since TensorBay supports copy operation between different datasets, users can use it to merge datasets.

Please see :ref:`examples/merge_datasets:Merge Datasets` example for more details.

**********************
 Get Label Statistics
**********************

TensorBay supports getting label statistics of dataset.

Please see :ref:`examples/get_label_statistics:Get Label Statistics` example for more details.
