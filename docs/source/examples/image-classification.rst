#################################
 Image with Classification Label
#################################

| **Classification** (:ref:`ref <supported_label_types:Classification>`) is a kind of label type.
  It represents the category of an image.
| Here, we take `Dogs vs. Cats`_ as an example to describe
  how to create, upload and read datasets with classification labels.

.. _dogs vs. cats: https://www.graviti.cn/open-datasets/DogsVsCats

**********************
 Create Local Dataset 
**********************

It takes two steps to create a dataset from local dataset files:

- Write the **catalog** (:ref:`ref <basic_concepts:catalog & subcatalog>`).
- Write the **dataloader**.

Write the Catalog File
======================

**Catalog** (:ref:`ref <basic_concepts:catalog & subcatalog>`) file is in json format,
which contains all label information of one dataset.

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/catalog.json
   :language: json
   :name: dogsvscats-catalog
   :linenos:

The only label type for `Dogs vs. Cats`_ is **classification**
(:ref:`ref <supported_label_types:Classification>`),
and there are totally 2 **categories** (:ref:`ref <supported_label_types:Category>`):
"cat" and "dog".

Write the Dataloader
====================

A **dataloader** is a function to read the original dataset files into a **dataset**
(:ref:`ref <basic_concepts:dataset>`). 

.. literalinclude:: ../../../tensorbay/opendataset/DogsVsCats/loader.py
   :language: python
   :name: dogsvscats-dataloader
   :linenos:

It takes mainly two steps to write a **dataloader**:

- Initialize **dataset** and **segments**.

  - Initialize **dataset** (:ref:`ref <basic_concepts:dataset>`).(L42)
  - Load **catalog** (:ref:`ref <basic_concepts:catalog & subcatalog>`).(L43)
  - Create **segments** (:ref:`ref <basic_concepts:segment>`).(L46)

- Initialize and append **data**.

  -  Initialize **data** (:ref:`ref <basic_concepts:data>`).(L49)
  -  Initialize **classification** (:ref:`ref <supported_label_types:Classification>`).(L51)
  -  Write **classification** into **data**.(L51)
  -  Append the **data** to the **segment**.(L52)

See :ref:`this page <supported_label_types:Classification>` for more label details.

Use Dataloaders from Community
==============================

You may also use **dataloaders** contributed by community to initialize **datasets**.

.. code:: python

   from tensorbay.opendataset import DogsVsCats

   dataset = DogsVsCats("path/to/dataset/directory")

.. note::

   Note that "DogsVsCats" is not the name,
   but the **identifier** of the dataset named "Dogs vs. Cats".
   **Identifier** is the name of a **dataloader** function.

.. warning::

   Dataloaders by community work well only with the original dataset directory structure.
   It is highly recommended to download datasets from either official website or
   `Graviti Opendatset Platform`_.
   See L26-35 of the :ref:`dataloader <dogsvscats-dataloader>`
   for the original dataset directory structure of `Dogs vs. Cats`_.

.. _graviti opendatset platform: https://www.graviti.cn/open-datasets


********************
 Read Local Dataset 
********************

TensorBay SDK provides two methods to get a **segment** (:ref:`ref <basic_concepts:segment>`)
from a **dataset** (:ref:`ref <basic_concepts:dataset>`).

.. code:: python 

   # get a segment by name.
   train_segment = dataset.get_segment_by_name("train")
   # get a segment by index.
   first_segment = dataset[0]

You can get a **data** inside a **segment** by index.

.. code:: python

   from PIL import Image

   data = train_segment[0]
   # read the label.
   category = data.label.classification.category
   image = Image.open(data.open())
   height, width = image.size
   image.show()

.. note::

   :meth:`~tensorbay.dataset.data.Data.open()` returns a file pointer like python open().


**********************
 Upload Local Dataset 
**********************

After creating a **dataset** (:ref:`ref <basic_concepts:dataset>`), you can use it locally,
or upload it to TensorBay for reuse and sharing.

.. code:: python

   dataset= gas.create_dataset("Dogs vs. Cats")
   dataset_client = gas.upload_dataset(dataset)
   dataset_client.commit()

Remember to do the :ref:`commit <features/version_control:Commit>` step after uploading.
Please see :ref:`version control <features/version_control:Version Control>` for more details.


************************
 Read TensorBay Dataset 
************************

| Now we can read the **dataset** (:ref:`ref <basic_concepts:dataset>`) uploaded in
  :ref:`examples/image-classification:Upload Local Dataset`.
| First of all, initialize a **GAS client** (:ref:`ref <features/tensorbay_client:GAS Client>`).

.. code:: python

    from tensorbay import GAS

    ACCESS_KEY = "Accesskey-*****"
    gas = GAS(ACCESS_KEY)

If you are not sure about the dataset name,
:meth:`GAS.list_dataset_names() <~tensorbay.client.gas.GAS.list_dataset_names()>`
can print all your uploaded datasets.

.. code:: python

   print(list(gas.list_dataset_names()))
   # ['Dogs vs. Cats']

.. note::
   The list method will also list all your forked (:ref:`ref <features/read_dataset:Read Dataset>`)
   **datasets**.

To get a **segment** (:ref:`ref <basic_concepts:segment>`), run:

.. code:: python

   from tensorbay.dataset import Segment

   dataset_client = gas.get_dataset("Dogs Vs. Cats")
   train_segment = Segment("train", dataset_client)

The **segment** you get now is the same as the one you get in
:ref:`examples/image-classification:Read Local Dataset`.
