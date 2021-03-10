##################
 TensorBay Client
##################

In Tensorbay SDK, we build different clients to handle different levels of operations.
In this topic, we mainly discuss GAS client and dataset client.
we use GAS client to perform operations on the dataset level
and use dataset client to perform operations inside a dataset.

************
 GAS Client
************

GAS is the abbreviation of Graviti AI Service.
GAS client is used for handling operations on the dataset level.
:numref:`Table. %s <gas_client_table>` lists the main methods of GAS client.

.. _gas_client_table:

.. table:: GAS Client methods
   :align: center
   :width: 70%

   ==========================================================   =========================================
                 Methods                                        Description
   ==========================================================   =========================================
   :meth:`~tensorbay.client.gas.GAS.create_dataset`             create a dataset with the given name
   :meth:`~tensorbay.client.gas.GAS.get_dataset`                get a dataset with the given name
   :meth:`~tensorbay.client.gas.GAS.get_dataset_id_and_type`    get ID and type of dataset with the given name
   :meth:`~tensorbay.client.gas.GAS.list_datasets`              list all forked datasets
   :meth:`~tensorbay.client.gas.GAS.upload_dataset`             upload a dataset to TensorBay
   :meth:`~tensorbay.client.gas.GAS.delete_dataset`             delete a dataset on TensorBay
   ==========================================================   =========================================

****************
 Dataset Client
****************

dataset client deals with the operations inside a dataset.
See :numref:`Table. %s <dataset_client_table>` for more details.

.. _dataset_client_table:

.. table:: Dataset Client
   :align: center
   :width: 70%

   ==========================================  ================================================================
   Objects to be Operated                       Methods
   ==========================================  ================================================================
   :ref:`basic_concepts:Segment`               :meth:`~tensorbay.client.dataset.DatasetClient.list_segment_names`
                                               :meth:`~tensorbay.client.dataset.DatasetClient.get_segment`
                                               :meth:`~tensorbay.client.dataset.DatasetClient.delete_segment`
   :ref:`basic_concepts:Catalog & SubCatalog`  :meth:`~tensorbay.client.dataset.DatasetClient.get_catalog`
                                               :meth:`~tensorbay.client.dataset.DatasetClient.upload_catalog`
   :ref:`basic_concepts:Dataset`               :meth:`~tensorbay.client.dataset.DatasetClient.commit`
                                               :meth:`~tensorbay.client.dataset.DatasetClient.update_information`
   ==========================================  ================================================================

Note that dataset and dataset client are different concepts.
Dataset (:ref:`ref <basic_concepts:dataset>`) represents a dataset entity.
While dataset client contains the information for determining a unique dataset on TensorBay
and supplies methods for dealing with it.
