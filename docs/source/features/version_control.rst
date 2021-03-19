#################
 Version Control
#################

TensorBay currently supports the linear version control.
A new version of a dataset can be built upon the previous version.
:numref:`Figure. %s <version_control>` demonstrates the relations
between different versions of a dataset.

.. _version_control:

.. figure:: ../images/version_control.png
   :scale: 60 %
   :align: center

   The relations between different versions of a dataset.


************************
 Create Draft And Commit
************************

The version control is based on the :ref:`draft <reference/glossary:Draft>` and
:ref:`commit <reference/glossary:Commit>`.

The :class:`~tensorbay.client.gas.GAS` is actually responsible for operating the datasets, while
the :class:`~tensorbay.client.dataset.DatasetClient` is for operating content of one dataset
in the draft or commit. A certain client can only work
in the draft or commit. Also, the dataset client supports the function of version control. You can create
and close the draft with the given methods in the dataset client.

.. code:: python

   from tensorbay import GAS

   ACCESS_KEY = "Accesskey-*****"
   gas = GAS(ACCESS_KEY)

   # dataset is the original dataset.
   # actually when calling "gas.upload_dataset(dataset.name)", a default draft "" is created.
   gas.create_dataset(dataset.name)
   dataset_client = gas.upload_dataset(dataset)
   dataset_client.commit("first_commit")

   # segment contains extra data that you want to add to the dataset.
   # create the draft.
   dataset_client.create_draft("draft-2")
   dataset_client.upload_segment(segment)
   # commit the draft and the draft will be deleted.
   dataset_client.commit("second_commit")


*********
 Checkout
*********

You can checkout to other draft with draft number or to commit with commit id through
:meth:`~tensorbay.client.dataset.DatasetClientBase.checkout`
in the :class:`~tensorbay.client.dataset.DatasetClient`. The draft number can be found through
:meth:`~tensorbay.client.dataset.DatasetClientBase.list_draft_titles_and_numbers` and the commit id can be can be found
through `the web page <https://gas.graviti.cn/>`_.

.. code:: python

   from tensorbay import GAS

   ACCESS_KEY = "Accesskey-*****"
   gas = GAS(ACCESS_KEY)

   dataset_client = gas.create_dataset(dataset.name)

   dataset_client.create_draft("draft-1")
   dataset_client.commit("first_commit")

   dataset_client.create_draft("draft-2")
   dataset_client.commit("second_commit")

   dataset_client.create_draft("draft-3")
   # list draft numbers.
   drafts = list(dataset_client.list_draft_titles_and_numbers())

   # checkout to the draft.
   dataset_client.checkout(draft_number=draft_number)
   # checkout to the commit.
   dataset_client.checkout(commit=commit_id)
