################################
 Text with Classification Label
################################


As demonstrated in :ref:`quick_start:Quick Start`,
:ref:`supported_label_types:Classification` supports classsification on images.
Besides images,
:ref:`supported_label_types:Classification` supports classification on text as well.

We take `20 Newsgroups`_ dataset as an example to illustrate the operations
for text dataset with classification labels.

.. _20 Newsgroups: https://www.graviti.cn/open-datasets/Newsgroups20

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

Here, we take `20 Newsgroups`_ as an example.

.. _obtain: https://docs.graviti.cn/guide/opendataset/get

.. _fork: https://docs.graviti.cn/guide/opendataset/fork

Reading a text dataset from TensorBay takes the same steps
as demonstrated in :ref:`quick_start:Quick Start`.

.. code:: python

    >>> dataset_client = gas.get_dataset("20 Newsgroups")

If you are not sure about the dataset name, you can visit our `Opendataset Platform`_ to check all
"forkable" open datasets.

.. _opendataset platform: https://www.graviti.cn/open-datasets

You can use the list method to get all the open datasets you forked.

.. code:: python

   >>> list(gas.list_dataset_names())
   ['Dogs vs. Cats', 'nuScenes', 'Neolix OD', "20 Newsgroups"]

In :ref:`basic_concepts:Dataset` ``20 Newsgroups``,
there are four :ref:`Segments<basic_concepts:Segment>`.

You can use the list method to get all the segment names under the
:ref:`features/tensorbay_client:Dataset Client`.

.. code:: python

    >>> list(dataset_client.list_segment_names())
    >>> ['20news-18828', '20news-bydate-test', '20news-bydate-train', '20_newsgroups']

And you can get a specific segment by passing the corresponding segment name.

.. code:: python

   >>> segment = dataset_client.get_segment_object("20_newsgroups")

In each :ref:`basic_concepts:Segment`, there is a sequence of :ref:`basic_concepts:Data`. You
can get one by index.

.. code:: python

   >>> data = segment[0]
   >>> data
   Data("tb:Newsgroups20_new:20_newsgroups://alt.atheism/49960.txt")(
     (fileuri): tb:Newsgroups20_new:20_newsgroups://alt.atheism/49960.txt,
     (labels): Labels(
       (classification): Classification(
         (category): 'alt.atheism'
       )
     )
   )

In each :ref:`basic_concepts:Data`,
there is one :ref:`supported_label_types:Classification` annotation.
You can get the annotation by the attrs of labels.

.. code:: python

   >>> label_classification = data.labels.classification
   >>> label_classification
   Classification(
     (category): 'alt.atheism'
   )
   >>> label_classification.category
   'alt.atheism'

There is only one label type in ``20 Newsgroups`` dataset, which is ``classification``.
The annotation "alt.atheism" is
stored in :ref:`supported_label_types:Category` of :ref:`supported_label_types:Classification`.

*************************
 Read Dataset from Local
*************************

If you want to read a dataset from local and there is an available :ref:`contribution:Dataloader`,
just import the dataloader function and pass the local dataset directory to it.

The directory structure for ``20 Newsgroups`` should be like:

.. code:: console

    <path>
        20news-18828/
            alt.atheism/
                49960
                51060
                51119
                51120
                ...
            comp.graphics/
            comp.os.ms-windows.misc/
            comp.sys.ibm.pc.hardware/
            comp.sys.mac.hardware/
            comp.windows.x/
            misc.forsale/
            rec.autos/
            rec.motorcycles/
            rec.sport.baseball/
            rec.sport.hockey/
            sci.crypt/
            sci.electronics/
            sci.med/
            sci.space/
            soc.religion.christian/
            talk.politics.guns/
            talk.politics.mideast/
            talk.politics.misc/
            talk.religion.misc/
        20news-bydate-test/
        20news-bydate-train/
        20_newsgroups/

.. code:: python

   >>> from graviti.opendataset import Newsgroups20

   >>> dataset = Newsgroups20("path/to/dataset/directory")
   >>> dataset
   Dataset("Newsgroups20") [
     Segment("20_newsgroups") [...],
     Segment("20news-18828") [...],
     Segment("20news-bydate-test") [...],
     Segment("20news-bydate-train") [...]
   ]

.. note::

   Note that ``Newsgroups20`` is not the name, but the :ref:`contribution:Identifier` of the dataset
   "20 Newsgroups". See :ref:`definition of identifier <contribution:Identifier>` for more details.

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

   >>> default_segment = dataset.get_segment_by_name("20_newsgroups")

   >>> first_segment = dataset[0]

The :ref:`basic_concepts:Segment` you get now is the same as the one you read from TensorBay in the
:ref:`quick_start:Read Dataset from TensorBay` part.

**************************
 Write Dataset Dataloader
**************************

If there is no :ref:`contribution:Dataloader` avaliable to your target dataset,
you can write one and contribute it.

Now we take ``20 Newsgroups`` as an example to explain how to write a dataloader
for datasets with text classification tasks.

Write the Catalog
=================

Before writing the dataloader, we first need to write the :ref:`contribution:Catalog`.

Catalog is a json file contains all label information of one dataset.
See :ref:`this page <basic_concepts:Catalog & SubCatalog>` for more details.
The only annotation type for ``20 Newsgroups`` is :ref:`supported_label_types:Classification`,
and there are 20 :ref:`supported_label_types:Category` types.

.. literalinclude:: ../../../tensorbay/opendataset/Newsgroups20/catalog.json
   :language: json
   :name: Newsgroups20-catalog
   :linenos:

.. note::

   The :ref:`categories<supported_label_types:Category>` in
   :ref:`basic_concepts:Dataset` ``20 Newsgroups`` have parent-child relationship,
   and it use "." to sparate different levels.

   Thus, ``categoryDelimeter`` is needed
   in the classification :ref:`Subcatalog <basic_concepts:Catalog & SubCatalog>`


Write the Dataloader
====================

The function of :ref:`contribution:Dataloader` is to read the dataset into a
:ref:`basic_concepts:Dataset` object.

The :ref:`code block <Newsgroups20-dataloader>` below displays the ``20 Newsgroups`` dataloader.

.. literalinclude:: ../../../tensorbay/opendataset/Newsgroups20/loader.py
   :language: python
   :name: Newsgroups20-dataloader
   :linenos:
   :emphasize-lines: 11-13, 16, 72, 76, 86

There are mainly two steps to write a :ref:`contribution:Dataloader`:

-  Create a :ref:`basic_concepts:Dataset` and its relevant :ref:`Segments <basic_concepts:Segment>`.
-  Add the :ref:`basic_concepts:Data` and
   corresponding :ref:`types of labels<supported_label_types:Supported Label Types>`
   to the created :ref:`Segments <basic_concepts:Segment>`.

Create Dataset and Segments
---------------------------

Note that after creating the :ref:`basic_concepts:Dataset`,
you need to load the :ref:`contribution:Catalog`.(L72)
The catalog file ``catalog.json`` is in the same directory with dataloader file.

In this example, there are four segments. We define ``SEGMENT_DESCRIPTION_DICT``
to store all the segment names and their corresponding descriptions(L16).

The segment names are also the folder names in the original dataset directory,
which makes sure only data under the folders with correct names is loaded(L76).


Add Data and Labels
-------------------

It takes four key substeps to add the data and the labels:

-  Creating :ref:`basic_concepts:Data` and adding content.
-  Creating :ref:`supported_label_types:Classification` and adding annotations.
-  Appending the Classification labels to the created Data.
-  Appending the Data to the created Segment.

See :ref:`this page <supported_label_types:Classification>`
for more details for about Classification annoation details.

.. note::
   The data in ``20 Newsgroups`` do not have extensions
   so that we add a "txt" extension to the remote path of each data file(L86)
   to ensure the loaded dataset could function well on TensorBay.

.. note::
   The :ref:`20 Newsgroups dataloader <Newsgroups20-dataloader>` above uses relative import(L11-13).
   However, when you write your own dataloader you should use regular import as shown below.
   And when you want to contribute your own dataloader, remember to use relative import.

.. code:: python

   >>> from graviti.dataset import Data, Dataset
   >>> from graviti.label import Classification

***********************************
 Upload Local Dataset to TensorBay
***********************************

Once you write your own :ref:`contribution:Dataloader` and read the local dataset into a
:ref:`basic_concepts:Dataset` object, you can upload it to TensorBay to share with the community.

.. code:: python

   >>> gas.create_dataset("20 Newsgroups")
   >>> dataset_client = gas.upload_dataset_object(dataset, jobs=8, skip_uploaded_files=False)
   >>> dataset_client.commit("20 Newsgroups")

Note that you need to create a dataset with the correct name on TensorBay first
if the :ref:`basic_concepts:Dataset` does not exist on TensorBay yet.

And remember to execute the :ref:`features/version_control:Commit` step after uploading.
If needed, you can re-upload and commit again.

Please see :ref:`features/version_control:Version Control` for more details.

.. note::

   Commit operation can alse be done on our GAS_ Platform.

.. _gas: https://www.graviti.cn/tensorBay

Please see :ref:`contribution:Contribution` for how to contribute your dataloader.
