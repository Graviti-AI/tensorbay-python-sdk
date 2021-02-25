##################
 TensorBay Client
##################

TensorBay provides two manners to use supported services.
The TensorBaySDK manner and the CLI manner.

In TensorBaySDK manner, we build different clients to handle different level operations.
Specifically,
we use :ref:`features/tensorbay_client:GAS Client` to process operations on dataset level
and :ref:`features/tensorbay_client:Dataset Client` to process operations inside a dataset.

************
 GAS Client
************

GAS is the abbreviation of Graviti AI Service.
:class:`GAS Client <~graviti.client.gas.GAS>` is used for handling operations
about user and datasets.
:numref:`Table. %s <gas client table>` lists the main methods of GAS Client.

.. _gas client table:

.. table:: GAS Client methods
   :align: center
   :width: 70%

   =====================================================  ===========================================
                 Methods                                  Description
   =====================================================  ===========================================
   :meth:`~graviti.client.gas.GAS.get_user_info`          get user information
   :meth:`~graviti.client.gas.GAS.create_dataset`         create a dataset with the given name
   :meth:`~graviti.client.gas.GAS.create_fusion_dataset`  create a fusion dataset with the given name
   :meth:`~graviti.client.gas.GAS.get_dataset`            get dataset with the given name
   :meth:`~graviti.client.gas.GAS.get_fusion_dataset`     get fusion dataset with the given name
   :meth:`~graviti.client.gas.GAS.list_datasets`          list all forked datasets
   :meth:`~graviti.client.gas.GAS.upload_dataset_object`  upload a dataset to TensorBay
   :meth:`~graviti.client.gas.GAS.delete_dataset`         delete a dataset on TensorBay
   =====================================================  ===========================================

****************
 Dataset Client
****************

:class:`Dataset Client <~graviti.client.dataset.DatasetClient>` deals with the operations
inside a :ref:`basic_concepts:Dataset`.
See :numref:`Table. %s <dataset_client>` for more details.

.. _dataset_client:

.. table:: Dataset Client
   :align: center
   :width: 70%

   ==========================================  ================================================================
   Ojects to be operated                       methods
   ==========================================  ================================================================
   :ref:`basic_concepts:Segment`               :meth:`~graviti.client.dataset.DatasetClient.list_segments`
                                               :meth:`~graviti.client.dataset.DatasetClient.get_segment_object`
                                               :meth:`~graviti.client.dataset.DatasetClient.delete_segments`
   :ref:`basic_concepts:Catalog & SubCatalog`  :meth:`~graviti.client.dataset.DatasetClient.get_catalog`
                                               :meth:`~graviti.client.dataset.DatasetClient.upload_catalog`
   :ref:`basic_concepts:Dataset`               :meth:`~graviti.client.dataset.DatasetClient.commit`
                                               :meth:`~graviti.client.dataset.DatasetClient.update_information`
   ==========================================  ================================================================

Note that :ref:`basic_concepts:Dataset` and :ref:`features/tensorbay_client:Dataset Client`
are different concepts.
:class:`Dataset` is a local concept. It represents a dataset entity created locally.
While :class:`DatasetClient` is a remote concept.
It contains the information for determining a unique dataset on TensorBay and supplies methods
for dealing with it.
