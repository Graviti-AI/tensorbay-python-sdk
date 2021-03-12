##############################
 Point Cloud with Box3D Label
##############################

:ref:`supported_label_types:Box3D` is a kind of label type. It represents the 3D Box labels on
point cloud. (:numref:`Fig. %s <example-Box3D>`)

.. _example-Box3D:

.. figure:: ../images/example-Box3D.png
   :scale: 100 %
   :align: center

   The preview of a point cloud file with Box3D annotations.

*************
 Preparation
*************

First of all, create a :ref:`features/tensorbay_client:GAS Client`.

.. code:: python

   >>> from graviti import GAS

   >>> ACCESS_KEY = "Accesskey-*****"
   >>> gas = GAS(ACCESS_KEY)

*****************************
 Read Dataset from TensorBay
*****************************

As mentioned in :ref:`quick_start:Quick Start`, obtain_ and fork_ should be done before reading a
dataset from TensorBay. Then, pass the correct dataset name to the GAS client, and you will get a
:ref:`features/tensorbay_client:Dataset Client`.

Here, we take `Neolix OD`_ as an example.

.. _fork: https://docs.graviti.cn/guide/opendataset/fork

.. _neolix od: https://www.graviti.cn/open-datasets/NeolixOD

.. _obtain: https://docs.graviti.cn/guide/opendataset/get

.. code:: python

   >>> dataset_client = gas.get_dataset("Neolix OD")

If you are not sure about the dataset name, you can visit our `Opendataset Platform`_ to check all
"forkable" open datasets.

.. _opendataset platform: https://www.graviti.cn/open-datasets

You can use the list method to print all your forked open datasets.

.. code:: python

   >>> list(gas.list_dataset_names())
   ['Dogs vs. Cats', 'nuScenes', 'Neolix PD']

In :ref:`basic_concepts:Dataset` ``Neolix OD``, there is one default :ref:`basic_concepts:Segment`
``""`` (empty string). You can get it by passing the segment name.

.. code:: python

   >>> from tensorbay.dataset import Segment
   >>> default_segment = Segment("", dataset_client)

In the default :ref:`basic_concepts:Segment`, there is a sequence of :ref:`basic_concepts:Data`. You
can get one by index.

.. code:: python

   >>> data = default_segment[0]
   >>> data
   Data("tb:Neolix OD:://000000.bin.gz")(
       (fileuri): tb:Neolix OD:://000000.bin.gz,
       (labels): Labels(
           (box3d): [
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...),
               LabeledBox3D(...)
           ]
       )
   )

.. note::

   If the :ref:`basic_concepts:segment` or
   :ref:`advanced_features/fusion_dataset/concepts:fusion segment` is created without
   given name, then its name will be "".

In each :ref:`basic_concepts:Data`,
there is a sequence of :ref:`supported_label_types:Box3D` annotations.
You can get one by index.

.. code:: python

   >>> label_box3d = data.label.box3d[0]
   >>> label_box3d
   LabeledBox3D(
       (translation): Vector3D(1.4035304, -0.8393294, 0.725594224),
       (rotation): Quaternion(-0.6885880829848394, 0.0, 0.0, -0.7251527094145509),
       (size): Vector3D(0.7573234, 0.7205151, 1.6880703),
       (category): 'Adult',
       (attributes): {...},
       (instance): ''
   )
   >>> label_box3d.category
   'Adult'
   >>> label_box3d.attributes
   {'Alpha': 0, 'Occlusion': 0, 'Truncation': False}

There is only one label type in ``Neolix OD`` dataset, which is ``box3d``. The annotation "Adult" is
stored in :ref:`supported_label_types:Category` of :ref:`supported_label_types:Box3D`.
The annotation "{'Alpha': 0, 'Occlusion': 0, 'Truncation': False}" is stored in
:ref:`supported_label_types:Attributes` of :ref:`supported_label_types:Box3D`.

*************************
 Read Dataset from Local
*************************

If you want to read a dataset from local and there is an available :ref:`contribution:Dataloader`,
just import the dataloader function and pass the local dataset directory to it. The directory
structure for ``Neolix OD`` should be like:

.. code:: console

   <path>
       bins/
           <id>.bin
           ...
           <id>.bin
       labels/
           <id>.txt
           ...
           <id>.txt

.. code:: python

   >>> from graviti.opendataset import NeolixOD

   >>> dataset = NeolixOD("path/to/dataset/directory")
   >>> dataset
   Dataset("Neolix OD") [
     Segment("") [...]
   ]

.. note::

   Note that ``NeolixOD`` is not the name, but the :ref:`contribution:Identifier` of the dataset
   "Neolix OD". See :ref:`definition of identifier <contribution:Identifier>` for more details.

.. note::

   Note that :ref:`basic_concepts:Dataset` and :ref:`features/tensorbay_client:Dataset Client`
   are different concepts.

.. warning::

   TensorBay dataloader works well only with the original dataset directory structure.
   Downloading datasets from either official website or `Graviti Opendatset Platform`_ is highly
   recommended.

.. _graviti opendatset platform: https://www.graviti.cn/open-datasets

TensorBay supplies two methods to fetch :ref:`basic_concepts:Segment` from
:ref:`basic_concepts:Dataset`.

.. code:: python

   >>> default_segment = dataset.get_segment_by_name("")

   >>> first_segment = dataset[0]

The :ref:`basic_concepts:Segment` you get now is the same as the one you read from TensorBay in the
:ref:`quick_start:Read Dataset from TensorBay` part.

**************************
 Write Dataset Dataloader
**************************

If there is no :ref:`contribution:Dataloader` avaliable to your target dataset,
you can write one and contribute it.
Now we take ``Neolix OD`` as an example to explain how to write a dataloader for datasets with Box3D
labels.

Write the Catalog
=================

Before writing the dataloader, we first need to write the :ref:`contribution:Catalog`.
Catalog is a json file contains all label information of one dataset.
See :ref:`this page <basic_concepts:Catalog & SubCatalog>` for more details.
The only annotation type for ``Neolix OD`` is :ref:`supported_label_types:Box3D`, and there are 15
:ref:`supported_label_types:Category` types and 3 :ref:`supported_label_types:Attributes` types.

.. literalinclude:: ../../../tensorbay/opendataset/NeolixOD/catalog.json
   :language: json
   :name: NeolixOD-catalog
   :linenos:


Write the Dataloader
====================

The function of :ref:`contribution:Dataloader` is to read the dataset into a
:ref:`basic_concepts:Dataset` object.
The :ref:`code block <NeolixOD-dataloader>` below displays the ``Neolix OD`` dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/NeolixOD/loader.py
   :language: python
   :name: NeolixOD-dataloader
   :linenos:
   :emphasize-lines: 11-13,35

There are mainly two steps to write a :ref:`contribution:Dataloader`:

-  Create a :ref:`basic_concepts:Dataset` and its relevant :ref:`Segments <basic_concepts:Segment>`.
-  Add the :ref:`basic_concepts:Data` and corresponding labels.
   to the created :ref:`Segments <basic_concepts:Segment>`.

Create Dataset and Segments
---------------------------

Note that after creating the :ref:`basic_concepts:Dataset`,
you need to load the :ref:`contribution:Catalog`.(L35)
The catalog file ``catalog.json`` is in the same directory with dataloader file.

In this example, we create a default segment without giving a specific name.
You can also create a segment by ``dataset.create_segment(SEGMENT_NAME)``.

Add Data and Labels
-------------------

It takes four key substeps to read the data and the labels:

-  Creating :ref:`basic_concepts:Data` and adding content.
-  Creating :ref:`supported_label_types:Box3D` and adding annotations.
-  Appending the Box3D labels to the created Data.
-  Appending the Data to the created Segment.

See :ref:`this page <supported_label_types:Box3D>` for more details for about
Box3D annoation details.

.. note::
   The :ref:`Neolix OD dataloader <NeolixOD-dataloader>` above uses relative import(L11-13).
   However, when you write your own dataloader you should use regular import as shown below.
   And when you want to contribute your own dataloader, remember to use relative import.

.. code:: python

   >>> from graviti.dataset import Data, Dataset
   >>> from graviti.label import LabeledBox3D

***********************************
 Upload Local Dataset to TensorBay
***********************************

Once you write your own :ref:`contribution:Dataloader` and read the local dataset into a
:ref:`basic_concepts:Dataset` object, you can upload it to TensorBay to share with the community.

.. code:: python

   >>> dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=False)
   >>> dataset_client.commit("Neolix OD")

Remember to execute the :ref:`features/version_control:Commit` step after uploading.
If needed, you can re-upload and commit again.
Please see :ref:`features/version_control:Version Control` for more details.

.. note::

   Commit operation can alse be done on our GAS_ Platform.

.. _gas: https://www.graviti.cn/tensorBay

Please see :ref:`contribution:Contribution` for how to contribute your dataloader.
