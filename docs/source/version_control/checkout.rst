##########
 Checkout
##########

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
   # list drafts.
   drafts = list(dataset_client.list_drafts())

   # checkout to the draft.
   dataset_client.checkout(draft_number=draft_number)
   # checkout to the commit.
   dataset_client.checkout(commit=commit_id)

