**************************************
 Getting Started with Version Control
**************************************

Commit
======

The basic element of TensorBay version control system is :ref:`reference/glossary:commit`.
Each commit of a TensorBay dataset is a **read-only** version.
Take the `VersionControlDemo Dataset <https://gas.graviti.cn/dataset/graviti-open-dataset/VersionControlDemo/branch/main>`_ as an example.

.. _commit-demonstration:

.. figure:: /images/commit.jpg
   :scale: 40 %
   :align: center

   The first two commits of dataset "VersionControlDemo".

.. note::
   "VersionControlDemo" is an open dataset on `Graviti Open Datasets <https://www.graviti.cn/>`_ platform,
   Please fork it before running the following demo code.

At the very beginning, there are only two commits in this dataset(:numref:`Fig. %s <commit-demonstration>`).
The code below checkouts to the first commit and check the data amount.

.. code:: python
   
   from tensorbay import GAS
   from tensorbay.dataset import Dataset

   gas = GAS("<YOUR_ACCESSKEY>")
   commits = dataset_client.list_commits()

   FIRST_COMMIT_ID = "ebb1cb46b36f4a4b922a40fb01574517"
   version_control_demo = Dataset("VersionControlDemo", gas, revision=FIRST_COMMIT_ID)
   train_segment = version_control_demo["train"]
   print(f"data amount: {len(train_segment)}.")
   # data amount: 4.

As shown above, there are 4 data in the train segment.

The code below checkouts to the second commit and check the data amount.

.. code:: python
   
   SECOND_COMMIT_ID = "6d003af913564943a83d705ff8440298"
   version_control_demo = Dataset("VersionControlDemo", gas, revision=SECOND_COMMIT_ID)
   train_segment = version_control_demo["train"]
   print(f"data amount: {len(train_segment)}.")
   # data amount: 8.

As shown above, there are 8 data in the train segment.

See :doc:`/features/version_control/draft_and_commit` for more details about commit.

Draft
=====

So how to create a dataset with multiple commits?
A commit comes from a :ref:`reference/glossary:draft`,
which is a concept that represents a **writable** workspace.

Typical steps to create a new commit:

- Create a draft.
- Do the modifications/update in this draft.
- Commit this draft into a commit.

Note that the first "commit" occurred in the third step above is a verb.
It means the action to turn a draft into a commit.

:numref:`Figure. %s <draft-demonstration>` demonstrates the relations between drafts and commits.

.. _draft-demonstration:

.. figure:: /images/draft.jpg
   :scale: 30 %
   :align: center

   The relations between a draft and commits.

The following code block creates a draft,
adds a new segment to the "VersionControlDemo" dataset and does the commit operation.

.. code:: python

   import os
   from tensorbay.dataset import Segment

   TEST_IMAGES_PATH = "<path/to/test_images>"

   dataset_client = gas.get_dataset("VersionControlDemo")
   dataset_client.create_draft("draft-1")

   test_segment = Segment("test")

   for image_name in os.listdir(TEST_IMAGES_PATH):
       data = Data(os.path.join(TEST_IMAGES_PATH, image_name))
       test_segment.append(data)

   dataset_client.upload_segment(test_segment, jobs=8)
   dataset_client.commit("add test segment")

See :doc:`/features/version_control/draft_and_commit` for more details about draft.

Tag
===

For the convenience of marking major commits and switching between different commits,
TensorBay provides the :ref:`reference/glossary:tag` concept.
The typical usage of tag is to mark released versions of a dataset.

The tag "v1.0.0" in :numref:`Fig. %s <commit-demonstration>` is added by

.. code:: python

   dataset_client.create_tag("v1.0.0", revision=SECOND_COMMIT_ID)

See :doc:`/features/version_control/tag` for more details about tag.

Branch
======

Sometimes, users may need to create drafts upon an early (not the latest) commit.
For example, in an algorithm team,
each team member may do modifications/update based on different versions of the dataset.
This means a commit list may turn into a commit tree.

For the convenience of maintaining a commit tree, TensorBay provides the :ref:`reference/glossary:branch` concept.

Actually, the commit list (:numref:`Fig. %s <commit-demonstration>`) above is the default branch named "main".

The code block below creates a branch "with-label" based on the :ref:`reference/glossary:revision` "v1.0.0",
and adds :doc:`classification </reference/label_format/Classification>` label to the "train" segment.

:numref:`Figure. %s <branch-demonstration>` demonstrates the two branches.

.. _branch-demonstration:

.. figure:: /images/branch.jpg
   :scale: 30 %
   :align: center

   The relations between branches.

.. code:: python

   from tensorbay.label import Catalog, Classification, ClassificationSubcatalog

   TRAIN_IMAGES_PATH = "<path/to/train/images>"

   catalog = Catalog()
   classification_subcatalog = ClassificationSubcatalog()
   classification_subcatalog.add_category("zebra")
   classification_subcatalog.add_category("horse")
   catalog.classification = classification_subcatalog

   dataset_client.upload_catalog(catalog)
   dataset_client.create_branch("with-label", revision="v1.0.0")
   dataset_client.create_draft("draft-2")

   train_segment = Segment("train")
   train_segment_client = dataset_client.get_segment(train_segment.name)

   for image_name in os.listdir(TRAIN_IMAGES_PATH):
       data = Data(os.path.join(TRAIN_IMAGES_PATH, image_name))
       data.label.classification = Classification(image_name[:5])
       train_segment.append(data)
       train_segment_client.upload_label(data)

   dataset_client.commit("add labels to train segment")

See :doc:`/features/version_control/branch` for more details about branch.
